import React, { useState, useEffect, useRef } from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Dimmer, Loader, Modal, Button, Icon, Message, Confirm } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import { useFormikContext } from "formik";
import axios from "axios";
import { useConfirmationModal } from "@js/oarepo_ui";

import { NewRequestModal, RequestModalContent } from "..";
import { REQUEST_TYPE } from "../../utils/objects";
import { useRequestsApi, useConfirmDialog } from "../../utils/hooks";

export const AcceptDeclineModal = ({ request, requestType, fetchNewRequests, triggerElement }) => {
  const {
    isOpen: isModalOpen,
    close: closeModal,
    open: openModal
  } = useConfirmationModal();
  const { sendRequest } = useRequestsApi();
  const { confirmDialogProps, confirmAction } = useConfirmDialog();

  const onSubmit = async (submitEvent) => {
    try {
      await submitEvent();
      closeModal();
      fetchNewRequests();
    } catch (e) { /* empty */ }
  };

  const acceptActionConfirmationHandler = () => confirmAction(() => onSubmit(() => sendRequest(request.links.actions.accept, REQUEST_TYPE.ACCEPT)), REQUEST_TYPE.ACCEPT);
  const declineActionConfirmationHandler = () => confirmAction(() => onSubmit(() => sendRequest(request.links.actions.decline, REQUEST_TYPE.DECLINE)), REQUEST_TYPE.DECLINE);

  const requestModalHeader = !_isEmpty(request?.title) ? request.title : (!_isEmpty(request?.name) ? request.name : request.type);

  return (
    <>
      <NewRequestModal
        header={requestModalHeader}
        isOpen={isModalOpen}
        closeModal={closeModal}
        openModal={openModal}
        trigger={triggerElement}
        actions={
          <>
            <Button title={i18next.t("Accept request")} onClick={acceptActionConfirmationHandler} positive icon labelPosition="left" floated="right">
              <Icon name="check" />
              {i18next.t("Accept")}
            </Button>
            <Button title={i18next.t("Decline request")} onClick={declineActionConfirmationHandler} negative icon labelPosition="left" floated="left">
              <Icon name="cancel" />
              {i18next.t("Decline")}
            </Button>
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