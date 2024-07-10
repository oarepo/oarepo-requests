import React, { useEffect, useRef } from "react";

import { useConfirmationModal } from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Dimmer, Loader, Modal, Button, Icon, Message, Confirm } from "semantic-ui-react";
import { useFormik, FormikProvider } from "formik";
import _isEmpty from "lodash/isEmpty";

import { mapPayloadUiToInitialValues } from "../utils";
import { ConfirmModalContextProvider, useRequestContext } from "../contexts";

/** 
 * @typedef {import("../types").Request} Request
 * @typedef {import("../types").RequestType} RequestType
 * @typedef {import("../types").RequestTypeEnum} RequestTypeEnum
 * @typedef {import("react").ReactElement} ReactElement
 * @typedef {import("semantic-ui-react").ConfirmProps} ConfirmProps
 */

/** @param {{ request: Request?, requestType: RequestType?, trigger: ReactElement, actions: [{ name: string, component: ReactElement }], ContentComponent: ReactElement }} props */
export const RequestModal = ({ request, requestType, trigger, actions, ContentComponent }) => {
  const errorMessageRef = useRef(null);
  const { requestTypes, fetchNewRequests } = useRequestContext();
  const {
    isOpen,
    close: closeModal,
    open: openModal,
  } = useConfirmationModal();

  const requestOrRequestType = request ?? requestType;
  requestType = request ? requestTypes.find(requestType => requestType.type_id === request.type) ?? {} : requestOrRequestType;

  const formik = useFormik({
    initialValues: 
      !_isEmpty(requestOrRequestType?.payload) ? 
        { payload: requestOrRequestType.payload } : 
        (requestOrRequestType?.payload_ui ? mapPayloadUiToInitialValues(requestOrRequestType?.payload_ui) : {}),
    onSubmit: () => { } // We'll redefine with customSubmitHandler
  });
  const {
    isSubmitting,
    resetForm,
    setErrors,
    errors,
  } = formik;

  const error = errors?.api;

  useEffect(() => {
    if (error) {
      errorMessageRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [error]);

  const onSubmit = async (asyncSubmitEvent, onError = () => {}) => {
    try {
      await asyncSubmitEvent();
      closeModal();
      fetchNewRequests();
    } catch (e) { 
      onError(e);
     }
  };

  const onClose = () => {
    closeModal();
    setErrors({});
    resetForm();
  };

  const header = !_isEmpty(requestOrRequestType?.title) ? requestOrRequestType.title : (!_isEmpty(requestOrRequestType?.name) ? requestOrRequestType.name : requestOrRequestType.type);
  const requestModalContentType = actions.some(({ name }) => name === "accept") ? "accept" : "submit";

  return (
    <FormikProvider value={formik}>
      <ConfirmModalContextProvider>
        {({ confirmDialogProps }) =>
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
              <Modal.Header as="h1" id="request-modal-header">{header}</Modal.Header>
              <Modal.Content>
                {error &&
                  <Message negative>
                    <Message.Header>{i18next.t("Error sending request")}</Message.Header>
                    <p ref={errorMessageRef}>{error?.message}</p>
                  </Message>
                }
                <ContentComponent request={requestOrRequestType} requestType={requestType} requestModalType={requestModalContentType} onCompletedAction={onSubmit} />
              </Modal.Content>
              <Modal.Actions>
                {actions.map(({ name, component: ActionComponent }) => 
                  <ActionComponent key={name} request={requestOrRequestType} requestType={requestType} onSubmit={onSubmit} />
                )}
                <Button onClick={onClose} icon labelPosition="left">
                  <Icon name="cancel" />
                  {i18next.t("Close")}
                </Button>
              </Modal.Actions>
            </Modal>
            <Confirm {...confirmDialogProps} />
          </>
        }
      </ConfirmModalContextProvider>
    </FormikProvider>
  );
};
