import React, { useState, useEffect, useContext, useRef } from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Dimmer, Loader, Segment, Modal, Button, Header, Icon, Message, Confirm } from "semantic-ui-react";
import { isEmpty } from "lodash";

import { useFormik, FormikContext } from "formik";
import axios from "axios";

import { RequestModalContent, CreateRequestModalContent } from ".";
import { REQUEST_TYPE } from "../utils/objects";
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
export const RequestModal = ({ request, requestTypes, requestModalType, isEventModal = false, triggerButton }) => {
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
  const [requests, setRequests] = useContext(RequestContext);
  const record = useContext(RecordContext);

  const formik = useFormik({
    initialValues: !isEmpty(request?.payload) ? { payload: request.payload } : mapPayloadUiToInitialValues(request?.payload_ui),
    onSubmit: (values) => {
      if (requestModalType === REQUEST_TYPE.SUBMIT) {
        confirmAction(REQUEST_TYPE.SUBMIT);
      } else if (requestModalType === REQUEST_TYPE.CREATE) {
        confirmAction(REQUEST_TYPE.CREATE);
      }
    }
  });

  useEffect(() => {
    if (error) {
      errorMessageRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [error]);

  const fetchUpdated = (url, setter) => {
    axios({
      method: 'get',
      url: url,
      headers: { 'Content-Type': 'application/json' }
    })
      .then(response => {
        console.log(response);
        setter(response.data);
      })
      .catch(error => {
        console.log(error);
      });
  }

  const callApi = async (url, method, doNotHandleResolve = false) => {
    if (doNotHandleResolve) {
      return axios({
        method: method,
        url: url,
        data: formik.values,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    return axios({
      method: method,
      url: url,
      data: formik.values,
      headers: { 'Content-Type': 'application/json' }
    })
      .then(response => {
        console.log(response);
        fetchUpdated(record.links?.requests, setRequests);
        setModalOpen(false);
        formik.resetForm();
      })
      .catch(error => {
        console.log(error);
        setError(error);
      })
      .finally(() => {
        formik.setSubmitting(false);
      });
  }

  const createAndSubmitRequest = async () => {
    try {
      await callApi(request.links.actions?.create, 'post', true);
      await callApi(request.links.actions?.submit, 'post', true);
      setModalOpen(false);
      formik.resetForm();
    } catch (error) {
      console.log(error);
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
    }
    return callApi(!isEventModal ? request.links.actions[requestType] : request.links[requestType], 'post');
  }

  const confirmAction = (requestType, createAndSubmit = false) => {
    console.log("confirmAction", requestType, createAndSubmit);
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
        break;
      case REQUEST_TYPE.CANCEL:
        newConfirmDialogProps.header = i18next.t("Delete request");
        newConfirmDialogProps.confirmButton = <Button negative>{i18next.t("Delete")}</Button>;
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
      console.log("createAndSubmit");
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

  const extraPreSubmitEvent = (event) => {
    if (event?.nativeEvent?.submitter?.name === "create-and-submit-request") {
      confirmAction(REQUEST_TYPE.SUBMIT, true);
    }
  }

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
        <Modal.Header as="h1" id="request-modal-header">{request.name}</Modal.Header>
        <Modal.Content>
          {error &&
            <Message negative>
              <Message.Header>{i18next.t("Error sending request")}</Message.Header>
              <p ref={errorMessageRef}>{error?.message}</p>
            </Message>
          }
          <FormikContext.Provider value={formik}>
            {requestModalType === REQUEST_TYPE.CREATE &&
              <CreateRequestModalContent requestType={request} extraPreSubmitEvent={extraPreSubmitEvent} /> ||
              <RequestModalContent request={request} requestTypes={requestTypes} requestModalType={requestModalType} />
            }
          </FormikContext.Provider>
        </Modal.Content>
        <Modal.Actions>
          {requestModalType === REQUEST_TYPE.SUBMIT &&
            <>
              <Button type="submit" form="request-form" title={i18next.t("Submit request")} color="blue" icon labelPosition="left" floated="right">
                <Icon name="paper plane" />
                {i18next.t("Submit")}
              </Button>
              <Button title={i18next.t("Delete request")} onClick={() => confirmAction(REQUEST_TYPE.CANCEL)} negative icon labelPosition="left" floated="left">
                <Icon name="trash alternate" />
                {i18next.t("Delete")}
              </Button>
              <Button title={i18next.t("Save drafted request")} onClick={() => sendRequest(REQUEST_TYPE.SAVE)} color="grey" icon labelPosition="left" floated="right">
                <Icon name="save" />
                {i18next.t("Save")}
              </Button>
            </>
          }
          {requestModalType === REQUEST_TYPE.CANCEL &&
            <Button title={i18next.t("Delete request")} onClick={() => confirmAction(REQUEST_TYPE.CANCEL)} negative icon labelPosition="left" floated="left">
              <Icon name="trash alternate" />
              {i18next.t("Delete")}
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
  requestModalType: PropTypes.oneOf(["create", "submit", "cancel", "accept"]).isRequired,
  requestTypes: PropTypes.array,
  isEventModal: PropTypes.bool,
  triggerButton: PropTypes.element,
};