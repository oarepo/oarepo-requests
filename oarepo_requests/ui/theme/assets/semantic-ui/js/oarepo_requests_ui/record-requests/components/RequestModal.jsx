import React, { useEffect, useRef, useState } from "react";
import { useConfirmationModal, serializeErrors } from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import {
  Dimmer,
  Loader,
  Modal,
  Button,
  Icon,
  Message,
  Confirm,
} from "semantic-ui-react";
import { useFormik, FormikProvider } from "formik";
import _isEmpty from "lodash/isEmpty";
import { mapPayloadUiToInitialValues } from "../utils";
import { ConfirmModalContextProvider, useRequestContext } from "../contexts";
import { REQUEST_TYPE, REQUEST_MODAL_TYPE } from "../utils/objects";
import { mapLinksToActions } from "./actions";

/**
 * @typedef {import("../types").Request} Request
 * @typedef {import("../types").RequestType} RequestType
 * @typedef {import("react").ReactElement} ReactElement
 */

/** @param {{ request: Request?, requestType: RequestType?, header: string | ReactElement, trigger: ReactElement, ContentComponent: ReactElement, requestCreationModal: Boolean }} props */

export const RequestModal = ({
  request,
  requestType,
  header,
  trigger,
  ContentComponent,
  requestCreationModal,
}) => {
  const errorMessageRef = useRef(null);
  const { fetchNewRequests, onErrorCallback, record } = useRequestContext();
  const { isOpen, close: closeModal, open: openModal } = useConfirmationModal();
  const [customFields, setCustomFields] = useState(null);
  const modalActions = mapLinksToActions(
    requestCreationModal ? requestType : request,
    customFields
  );
  console.log(record);
  const formik = useFormik({
    initialValues:
      request && !_isEmpty(request?.payload)
        ? { payload: request.payload }
        : requestType?.payload_ui
        ? mapPayloadUiToInitialValues(customFields)
        : {},
    onSubmit: () => {}, // We'll redefine with customSubmitHandler
  });
  const {
    isSubmitting,
    resetForm,
    setErrors,
    errors,
    setFieldError,
    setSubmitting,
  } = formik;

  const error = errors?.api;

  useEffect(() => {
    if (error) {
      errorMessageRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [error]);

  useEffect(() => {
    fetch("http://localhost:3001/form/config")
      .then((response) => response.json())
      .then((data) => setCustomFields(data.custom_fields));
  }, []);

  const onSubmit = async (asyncSubmitEvent, onError, requestActionType) => {
    setSubmitting(true);
    setErrors({});
    try {
      await asyncSubmitEvent();
      closeModal();
      fetchNewRequests();
    } catch (e) {
      // for use to communicate to outside react app
      console.log("catch start");
      if (onErrorCallback) {
        onErrorCallback(e);
      }
      // callback to be used specifically for some calls inside of the component
      if (onError) {
        onError(e);
      } else {
        if (requestActionType === REQUEST_TYPE.CREATE) {
          if (e.response?.data?.errors?.length > 0) {
            const now = new Date();
            const validationErrors = {
              value: serializeErrors(e.response?.data?.errors),
              expiry: now.getTime() + 10000,
            };
            localStorage.setItem(
              `validationErrors.${record.id}`,
              JSON.stringify(validationErrors)
            );
            setFieldError(
              "api",
              i18next.t(
                "The request could not be created, due to draft validation errors. Redirecting to edit page..."
              )
            );
            setTimeout(() => {
              window.location.href = record.links.edit_html;
            }, 2000);
          } else {
            setFieldError(
              "api",
              i18next.t("The request could not be created.")
            );
          }
        } else if (requestActionType === REQUEST_TYPE.SUBMIT) {
          setFieldError(
            "api",
            i18next.t("The request could not be submitted.")
          );
        } else {
          setFieldError(
            "api",
            i18next.t(
              "The action was not executed successfully. Please try again."
            )
          );
        }
      }
    } finally {
      setSubmitting(false);
    }
  };

  const onClose = () => {
    closeModal();
    setErrors({});
    resetForm();
  };

  // Only applies to RequestModalContent component:
  // READ ONLY modal type contains Accept, Decline, and/or Cancel actions OR contains Cancel action only => only ReadOnlyCustomFields are rendered
  // SUBMIT FORM modal type contains Submit and/or Save, Create, CreateAndSubmit action => Form is rendered
  const requestModalContentType = modalActions.some(
    ({ name }) => name === REQUEST_TYPE.ACCEPT || name === REQUEST_TYPE.CANCEL
  )
    ? REQUEST_MODAL_TYPE.READ_ONLY
    : REQUEST_MODAL_TYPE.SUBMIT_FORM;

  return (
    <FormikProvider value={formik}>
      <ConfirmModalContextProvider>
        {({ confirmDialogProps }) => (
          <>
            <Modal
              className="requests-request-modal"
              as={Dimmer.Dimmable}
              blurring
              onClose={onClose}
              onOpen={openModal}
              open={isOpen}
              trigger={trigger || <Button content="Open Modal" />}
              closeIcon
              closeOnDocumentClick={false}
              closeOnDimmerClick={false}
              role="dialog"
              aria-labelledby="request-modal-header"
              aria-describedby="request-modal-desc"
            >
              <Dimmer active={isSubmitting}>
                <Loader inverted size="large" />
              </Dimmer>
              <Modal.Header as="h1" id="request-modal-header">
                {header}
              </Modal.Header>
              <Modal.Content>
                {error && (
                  <Message negative>
                    <Message.Header>{error}</Message.Header>
                  </Message>
                )}
                <ContentComponent
                  request={request}
                  requestType={requestType}
                  requestModalType={requestModalContentType}
                  onCompletedAction={onSubmit}
                  customFields={customFields}
                />
              </Modal.Content>
              <Modal.Actions>
                {modalActions.map(({ name, component: ActionComponent }) => (
                  <ActionComponent
                    key={name}
                    request={request}
                    requestType={requestType}
                    onSubmit={onSubmit}
                  />
                ))}
                <Button onClick={onClose} icon labelPosition="left">
                  <Icon name="cancel" />
                  {i18next.t("Close")}
                </Button>
              </Modal.Actions>
            </Modal>
            <Confirm {...confirmDialogProps} />
          </>
        )}
      </ConfirmModalContextProvider>
    </FormikProvider>
  );
};
