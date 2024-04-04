import React, { useState, useEffect, useContext, useRef } from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Dimmer, Loader, Modal, Button, Icon, Message, Confirm } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import _isFunction from "lodash/isFunction";

import { useFormik, FormikContext } from "formik";
import axios from "axios";

import { RequestModalContent, CreateRequestModalContent } from ".";
import { REQUEST_TYPE } from "../utils/objects";
import { isDeepEmpty } from "../utils";
import { RecordContext, RequestContext } from "../contexts";

/** 
 * @typedef {import("../types").Request} Request
 * @typedef {import("../types").RequestType} RequestType
 * @typedef {import("../types").RequestTypeEnum} RequestTypeEnum
 * @typedef {import("react").ReactElement} ReactElement
 * @typedef {import("semantic-ui-react").ConfirmProps} ConfirmProps
 */

const mapPayloadUiToInitialValues = (payloadUi) => {
  const initialValues = { payload: {} };
  payloadUi?.forEach(section => {
    section.fields.forEach(field => {
      initialValues.payload[field.field] = "";
    });
  });
  return initialValues;
};

/** @param {{ request: Request, requestTypes: RequestType[], requestModalType: RequestTypeEnum, isEventModal: boolean, triggerButton: ReactElement }} props */
export const RequestModal = ({ request, requestTypes, requestModalType, isEventModal = false, triggerButton, fetchNewRequests }) => {
  const [modalOpen, setModalOpen] = useState(false);
  const [error, setError] = useState(null);

  /** @type {[ConfirmProps, (props: ConfirmProps) => void]} */
  const [confirmDialogProps, setConfirmDialogProps] = useState({
    open: false,
    content: i18next.t("Are you sure?"),
    cancelButton: i18next.t("Cancel"),
    confirmButton: i18next.t("OK"),
    onCancel: () => setConfirmDialogProps(props => ({ ...props, open: false })),
    onConfirm: () => setConfirmDialogProps(props => ({ ...props, open: false }))
  });

  const errorMessageRef = useRef(null);

  /** @type {[Request[], (requests: Request[]) => void]} */
  const { setRequests } = useContext(RequestContext);
  const { record, setRecord } = useContext(RecordContext);

  const formik = useFormik({
    initialValues: !_isEmpty(request?.payload) ? { payload: request.payload } : (request?.payload_ui ? mapPayloadUiToInitialValues(request?.payload_ui) : {}),
    onSubmit: () => {}
  });

  useEffect(() => {
    if (error) {
      errorMessageRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [error]);

  const callApi = async (url, method, data = formik.values, doNotHandleResolve = false) => {
    if (_isEmpty(url)) {
      setError(new Error(i18next.t("Cannot send request. Please try again later.")));
      formik.setSubmitting(false);
      return;
    }

    if (doNotHandleResolve) {
      return axios({
        method: method,
        url: url,
        data: data,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    return axios({
      method: method,
      url: url,
      data: data,
      headers: { 'Content-Type': 'application/json' }
    })
      .then(response => {
        fetchNewRequests();
        setModalOpen(false);
        formik.resetForm();
      })
      .catch(error => {
        console.error(error);
        setError(error);
      })
      .finally(() => {
        formik.setSubmitting(false);
      });
  }

  const createAndSubmitRequest = async () => {
    try {
      const createdRequest = await callApi(request.links.actions?.create, 'post', formik.values, true);
      await callApi(createdRequest.data?.links?.actions?.submit, 'post', {}, true);
      fetchNewRequests();
      setModalOpen(false);
      formik.resetForm();
    } catch (error) {
      console.error(error);
      setError(error);
    } finally {
      formik.setSubmitting(false);
    }
  }

  const sendRequest = async (requestType, createAndSubmit = false) => {
    formik.setSubmitting(true);
    setError(null);
    if (createAndSubmit) {
      return createAndSubmitRequest();
    }
    if (requestType === REQUEST_TYPE.SAVE) {
      return callApi(request.links.self, 'put');
    } else if (requestType === REQUEST_TYPE.ACCEPT) { // Reload page after succesful "Accept" operation
      await callApi(request.links.actions?.accept, 'post');
      location.reload();
      return;
    }
    const mappedData = !isDeepEmpty(formik.values) ? {} : formik.values;
    const actionUrl = !isEventModal ? request.links.actions[requestType] : request.links[requestType];
    return callApi(actionUrl, 'post', mappedData);
  }

  const confirmAction = (requestType, createAndSubmit = false) => {
    /** @type {ConfirmProps} */
    let newConfirmDialogProps = {
      open: true,
      onConfirm: () => {
        setConfirmDialogProps(props => ({ ...props, open: false }));
        sendRequest(requestType);
      },
      onCancel: () => {
        setConfirmDialogProps(props => ({ ...props, open: false }));
        formik.setSubmitting(false);
      }
    };

    switch (requestType) {
      case REQUEST_TYPE.CREATE:
        newConfirmDialogProps.header = isEventModal ? i18next.t("Submit event") : i18next.t("Create request");
        break;
      case REQUEST_TYPE.SUBMIT:
        newConfirmDialogProps.header = i18next.t("Submit request");
        newConfirmDialogProps.confirmButton = i18next.t("OK");
        break;
      case REQUEST_TYPE.CANCEL:
        newConfirmDialogProps.header = i18next.t("Cancel request");
        newConfirmDialogProps.confirmButton = <Button negative>{i18next.t("Cancel request")}</Button>;
        break;
      case REQUEST_TYPE.ACCEPT:
        newConfirmDialogProps.header = i18next.t("Accept request");
        newConfirmDialogProps.confirmButton = <Button positive>{i18next.t("Accept")}</Button>;
        break;
      case REQUEST_TYPE.DECLINE:
        newConfirmDialogProps.header = i18next.t("Decline request");
        newConfirmDialogProps.confirmButton = <Button negative>{i18next.t("Decline")}</Button>;
        break;
      default:
        break;
    }

    if (createAndSubmit) {
      newConfirmDialogProps = {
        ...newConfirmDialogProps,
        header: i18next.t("Create and submit request"),
        confirmButton: <Button positive>{i18next.t("Create and submit")}</Button>,
        onConfirm: () => {
          setConfirmDialogProps(props => ({ ...props, open: false }));
          sendRequest(REQUEST_TYPE.CREATE, createAndSubmit);
        }
      }
    }

    setConfirmDialogProps(props => ({ ...props, ...newConfirmDialogProps }));
  }

  const onClose = () => {
    setModalOpen(false);
    setError(null);
    formik.resetForm();
  }

  const customSubmitHandler = async (submitButtonName) => {
    try {
      await formik.submitForm();
      if (submitButtonName === "create-and-submit-request") {
        confirmAction(REQUEST_TYPE.SUBMIT, true);
        return;
      }
      if (requestModalType === REQUEST_TYPE.SUBMIT) {
        confirmAction(REQUEST_TYPE.SUBMIT);
      } else if (requestModalType === REQUEST_TYPE.CREATE) {
        sendRequest(REQUEST_TYPE.CREATE);
      }
    } catch (error) {
      console.error(error);
      setError(error);
    } finally {
      formik.setSubmitting(false);
    }
  }

  const requestType = requestTypes?.find(requestType => requestType.type_id === request.type) ?? {};
  const formWillBeRendered = requestModalType === REQUEST_TYPE.SUBMIT && requestType?.payload_ui;
  const submitButtonExtraProps = formWillBeRendered ? { type: "submit", form: "request-form" } : { onClick: () => confirmAction(REQUEST_TYPE.SUBMIT) };
  const requestModalHeader = !_isEmpty(request?.title) ? request.title : (!_isEmpty(request?.name) ? request.name : request.type);

  return (
    <>
      <Modal
        className="requests-request-modal"
        as={Dimmer.Dimmable}
        blurring
        onClose={onClose}
        onOpen={() => setModalOpen(true)}
        open={modalOpen}
        trigger={triggerButton || <Button content="Open Modal" />}
        closeIcon
        closeOnDocumentClick={false}
        closeOnDimmerClick={false}
        role="dialog"
        aria-labelledby="request-modal-header"
        aria-describedby="request-modal-desc"
      >
        <Dimmer active={formik.isSubmitting}>
          <Loader inverted size="large" />
        </Dimmer>
        <Modal.Header as="h1" id="request-modal-header">{requestModalHeader}</Modal.Header>
        <Modal.Content>
          {error &&
            <Message negative>
              <Message.Header>{i18next.t("Error sending request")}</Message.Header>
              <p ref={errorMessageRef}>{error?.message}</p>
            </Message>
          }
          <FormikContext.Provider value={formik}>
            {requestModalType === REQUEST_TYPE.CREATE &&
              <CreateRequestModalContent requestType={request} customSubmitHandler={customSubmitHandler} /> ||
              <RequestModalContent request={request} requestType={requestType} requestModalType={requestModalType} customSubmitHandler={customSubmitHandler} />
            }
          </FormikContext.Provider>
        </Modal.Content>
        <Modal.Actions>
          {requestModalType === REQUEST_TYPE.SUBMIT &&
            <>
              <Button title={i18next.t("Submit request")} color="blue" icon labelPosition="left" floated="right" {...submitButtonExtraProps}>
                <Icon name="paper plane" />
                {i18next.t("Submit")}
              </Button>
              <Button title={i18next.t("Cancel request")} onClick={() => confirmAction(REQUEST_TYPE.CANCEL)} negative icon labelPosition="left" floated="left">
                <Icon name="trash alternate" />
                {i18next.t("Cancel request")}
              </Button>
              <Button title={i18next.t("Save drafted request")} onClick={() => sendRequest(REQUEST_TYPE.SAVE)} color="grey" icon labelPosition="left" floated="right">
                <Icon name="save" />
                {i18next.t("Save")}
              </Button>
            </>
          }
          {requestModalType === REQUEST_TYPE.CANCEL &&
            <Button title={i18next.t("Cancel request")} onClick={() => confirmAction(REQUEST_TYPE.CANCEL)} negative icon labelPosition="left" floated="left">
              <Icon name="trash alternate" />
              {i18next.t("Cancel request")}
            </Button>
          }
          {requestModalType === REQUEST_TYPE.ACCEPT &&
            <>
              <Button title={i18next.t("Accept request")} onClick={() => confirmAction(REQUEST_TYPE.ACCEPT)} positive icon labelPosition="left" floated="right">
                <Icon name="check" />
                {i18next.t("Accept")}
              </Button>
              <Button title={i18next.t("Decline request")} onClick={() => confirmAction(REQUEST_TYPE.DECLINE)} negative icon labelPosition="left" floated="left">
                <Icon name="cancel" />
                {i18next.t("Decline")}
              </Button>
            </>
          }
          {requestModalType === REQUEST_TYPE.CREATE && (!isEventModal &&
            <>
              <Button type="submit" form="request-form" name="create-request" title={i18next.t("Create request")} color="blue" icon labelPosition="left" floated="right">
                <Icon name="plus" />
                {i18next.t("Create")}
              </Button>
              <Button type="submit" form="request-form" name="create-and-submit-request" title={i18next.t("Submit request")} color="blue" icon labelPosition="left" floated="left">
                <Icon name="paper plane" />
                {i18next.t("Submit")}
              </Button>
            </> ||
            <Button type="submit" form="request-form" name="create-event" title={i18next.t("Submit")} color="blue" icon labelPosition="left" floated="left">
              <Icon name="plus" />
              {i18next.t("Submit")}
            </Button>)
          }
          <Button onClick={onClose} icon labelPosition="left">
            <Icon name="cancel" />
            {i18next.t("Cancel")}
          </Button>
        </Modal.Actions>
        <Confirm {...confirmDialogProps} />
      </Modal>
    </>
  );
};

RequestModal.propTypes = {
  request: PropTypes.object.isRequired,
  requestModalType: PropTypes.oneOf(["create", "submit", "cancel", "accept", "view_only"]).isRequired,
  requestTypes: PropTypes.array,
  isEventModal: PropTypes.bool,
  triggerButton: PropTypes.element,
};