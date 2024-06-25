import React, { useState, useEffect, useRef } from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Dimmer, Loader, Modal, Button, Icon, Message, Confirm } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import { useFormik, FormikContext } from "formik";
import axios from "axios";
import { useConfirmationModal } from "@js/oarepo_ui";

import { RequestModal } from "..";
import { REQUEST_TYPE } from "../../utils/objects";
import { useRequestsApi, useConfirmDialog } from "../../utils/hooks";

export const SubmitModal = ({ request, requestType, fetchNewRequests, triggerElement }) => {
  const {
    isOpen: isModalOpen,
    close: closeModal,
  } = useConfirmationModal();
  const { sendRequest } = useRequestsApi();
  const { confirmAction } = useConfirmDialog();

  const onConfirm = async (requestType) => {
    try {
      await sendRequest(requestType);
      closeModal();
      fetchNewRequests();
    } catch (e) { /* empty */ }
  };

  const formWillBeRendered = !_isEmpty(requestType?.payload_ui);
  const submitButtonExtraProps = formWillBeRendered ? { type: "submit", form: "request-form" } : { onClick: () => confirmAction(REQUEST_TYPE.SUBMIT) };

  return (
    <RequestModal
      key={request.id}
      request={request}
      requestType={requestType}
      requestModalType={REQUEST_TYPE.SUBMIT}
      isOpen={isModalOpen}
      closeModal={closeModal}
      fetchNewRequests={fetchNewRequests}
      triggerButton={triggerElement}
      actions={
        <>
          <Button title={i18next.t("Submit request")} color="blue" icon labelPosition="left" floated="right" {...submitButtonExtraProps}>
            <Icon name="paper plane" />
            {i18next.t("Submit")}
          </Button>
          <Button title={i18next.t("Cancel request")} onClick={() => confirmAction(onConfirm, REQUEST_TYPE.CANCEL)} negative icon labelPosition="left" floated="left">
            <Icon name="trash alternate" />
            {i18next.t("Cancel request")}
          </Button>
          {formWillBeRendered && 
            <Button title={i18next.t("Save drafted request")} onClick={() => sendRequest(REQUEST_TYPE.SAVE)} color="grey" icon labelPosition="left" floated="right">
              <Icon name="save" />
              {i18next.t("Save")}
            </Button>
          }
        </>
      }
    />
  );
}