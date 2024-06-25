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

export const SubmitModal = ({ request, requestType, fetchNewRequests, triggerElement }) => {
  const {
    isOpen: isModalOpen,
    close: closeModal,
  } = useConfirmationModal();
  const { sendRequest } = useRequestsApi();
  const { confirmDialogProps, confirmAction } = useConfirmDialog();
  const { setSubmitting, submitForm, setErrors } = useFormikContext();

  const customSubmitHandler = async (submitButtonName) => {
    try {
      await submitForm();
      confirmAction(sendRequest, REQUEST_TYPE.SUBMIT);
    } catch (error) {
      setErrors({ api: error });
    } finally {
      setSubmitting(false);
    }
  }

  const onConfirm = async (requestType) => {
    try {
      await sendRequest(requestType);
      closeModal();
      fetchNewRequests();
    } catch (e) { /* empty */ }
  };

  const formWillBeRendered = !_isEmpty(requestType?.payload_ui);
  const submitButtonExtraProps = formWillBeRendered ? { type: "submit", form: "request-form" } : { onClick: () => confirmAction(onConfirm, REQUEST_TYPE.SUBMIT) };

  return (
    <>
      <NewRequestModal
        key={request.id}
        request={request}
        isOpen={isModalOpen}
        closeModal={closeModal}
        trigger={triggerElement}
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
        content={
          <RequestModalContent request={request} requestType={requestType} requestModalType={REQUEST_TYPE.SUBMIT} customSubmitHandler={customSubmitHandler} />
        }
      />
      <Confirm {...confirmDialogProps} />
    </>
  );
}