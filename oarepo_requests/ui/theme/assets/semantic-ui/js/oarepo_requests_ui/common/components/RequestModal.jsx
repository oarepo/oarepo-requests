import React from "react";
import { useConfirmationModal } from "@js/oarepo_ui";
import { Dimmer, Modal, Button } from "semantic-ui-react";
import { Formik } from "formik";
import _isEmpty from "lodash/isEmpty";
import PropTypes from "prop-types";
import {
  useCallbackContext,
  useFormikRefContext,
  RequestConfigContextProvider,
  ModalControlContextProvider,
} from "../contexts";
import { RequestModalContentAndActions } from "./RequestModalContentAndActions";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
/**
 * @typedef {import("../../record-requests/types").Request} Request
 * @typedef {import("../../record-requests/types").RequestType} RequestType
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
  const { isOpen, close: closeModal, open: openModal } = useConfirmationModal();
  const { setActionsLocked } = useCallbackContext();
  const formikRef = useFormikRefContext();

  const { resetForm, setErrors } = formikRef?.current || {};

  const requestTypeId = requestType?.type_id || request?.type;
  const onClose = () => {
    setErrors?.({});
    resetForm?.();
    closeModal();
    setActionsLocked(false);
  };
  return (
    <Formik
      initialValues={
        _isEmpty(request?.payload)
          ? { payload: {} }
          : { payload: request.payload }
      }
      innerRef={formikRef}
    >
      <ModalControlContextProvider
        value={{
          isOpen,
          closeModal: onClose,
          openModal,
        }}
      >
        <Modal
          className="requests-request-modal form-modal"
          as={Dimmer.Dimmable}
          blurring
          size="large"
          onClose={onClose}
          onOpen={openModal}
          open={isOpen}
          trigger={trigger || <Button content="Open Modal" />}
          closeIcon
          closeOnDocumentClick={false}
          closeOnDimmerClick={false}
          aria-labelledby="request-modal-header"
          aria-describedby="request-modal-desc"
        >
          <Modal.Header as="h1" id="request-modal-header">
            {header}{" "}
            {request?.id && (
              <a
                target="_blank"
                rel="noopener noreferrer"
                href={request?.links?.self_html}
                className="text size small"
              >
                ({i18next.t("request details")})
              </a>
            )}
          </Modal.Header>
          <RequestConfigContextProvider requestTypeId={requestTypeId}>
            <RequestModalContentAndActions
              request={request}
              requestType={requestType}
              ContentComponent={ContentComponent}
              requestCreationModal={requestCreationModal}
              onClose={onClose}
              formikRef={formikRef}
            />
          </RequestConfigContextProvider>
        </Modal>
      </ModalControlContextProvider>
    </Formik>
  );
};

RequestModal.propTypes = {
  request: PropTypes.object,
  requestType: PropTypes.object,
  header: PropTypes.oneOfType([PropTypes.string, PropTypes.element]),
  trigger: PropTypes.element,
  ContentComponent: PropTypes.func,
  requestCreationModal: PropTypes.bool,
};
