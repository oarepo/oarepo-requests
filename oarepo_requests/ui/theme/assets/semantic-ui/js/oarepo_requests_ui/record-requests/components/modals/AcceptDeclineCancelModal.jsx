import React from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon, Confirm } from "semantic-ui-react";

import { RequestModal, RequestModalContent } from "..";
import { REQUEST_TYPE } from "../../utils/objects";
import { useRequestsApi, useConfirmDialog, useRequestModal } from "../../utils/hooks";
import { useRequestContext } from "../../contexts";

export const AcceptDeclineCancelModal = ({ request, requestType, triggerElement, modalHeader }) => {
  const { fetchNewRequests } = useRequestContext();
  const {
    isOpen: isModalOpen,
    close: closeModal,
    open: openModal,
    onSubmit
  } = useRequestModal(fetchNewRequests);
  const { sendRequest } = useRequestsApi();
  const { confirmDialogProps, confirmAction } = useConfirmDialog();

  const acceptActionConfirmationHandler = () => confirmAction(() => onSubmit(() => sendRequest(request.links.actions?.accept, REQUEST_TYPE.ACCEPT)), REQUEST_TYPE.ACCEPT);
  const declineActionConfirmationHandler = () => confirmAction(() => onSubmit(() => sendRequest(request.links.actions?.decline, REQUEST_TYPE.DECLINE)), REQUEST_TYPE.DECLINE);
  const cancelActionConfirmationHandler = () => confirmAction(() => onSubmit(() => sendRequest(request.links.actions?.cancel, REQUEST_TYPE.CANCEL)), REQUEST_TYPE.CANCEL);

  return (
    <>
      <RequestModal
        header={modalHeader}
        isOpen={isModalOpen}
        closeModal={closeModal}
        openModal={openModal}
        trigger={triggerElement}
        actions={
          <>
            {request.links.actions?.accept && <Button title={i18next.t("Accept request")} onClick={acceptActionConfirmationHandler} positive icon labelPosition="left" floated="right">
              <Icon name="check" />
              {i18next.t("Accept")}
            </Button>}
            {request.links.actions?.decline && <Button title={i18next.t("Decline request")} onClick={declineActionConfirmationHandler} negative icon labelPosition="left" floated="left">
              <Icon name="cancel" />
              {i18next.t("Decline")}
            </Button>}
            {request.links.actions?.cancel && <Button title={i18next.t("Cancel request")} onClick={cancelActionConfirmationHandler} color="grey" icon labelPosition="left" floated="left">
              <Icon name="trash alternate" />
              {i18next.t("Cancel request")}
            </Button>}
          </>
        }
        content={
          <RequestModalContent request={request} requestType={requestType} requestModalType={REQUEST_TYPE.ACCEPT} />
        }
      />
      <Confirm {...confirmDialogProps} />
    </>
  );
}