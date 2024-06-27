import React from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon, Confirm } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import { useFormikContext } from "formik";

import { NewRequestModal, RequestModalContent } from "..";
import { REQUEST_TYPE } from "../../utils/objects";
import { useRequestsApi, useConfirmDialog, useRequestModal } from "../../utils/hooks";

export const SubmitModal = ({ request, requestType, fetchNewRequests, triggerElement, modalHeader }) => {
  const {
    isOpen: isModalOpen,
    close: closeModal,
    open: openModal,
    onSubmit
  } = useRequestModal(fetchNewRequests);
  const { sendRequest } = useRequestsApi();
  const { confirmDialogProps, confirmAction } = useConfirmDialog();
  const { setSubmitting, submitForm, setErrors } = useFormikContext();

  const submitActionConfirmationHandler = () => confirmAction(() => onSubmit(() => sendRequest(request.links.actions.submit, REQUEST_TYPE.SUBMIT)), REQUEST_TYPE.SUBMIT);

  const customSubmitHandler = async () => {
    try {
      await submitForm();
      submitActionConfirmationHandler();
    } catch (error) {
      setErrors({ api: error });
    } finally {
      setSubmitting(false);
    }
  };

  const formWillBeRendered = !_isEmpty(requestType?.payload_ui);
  const submitButtonExtraProps = formWillBeRendered ? { type: "submit", form: "request-form" } : { onClick: submitActionConfirmationHandler };

  return (
    <>
      <NewRequestModal
        header={modalHeader}
        isOpen={isModalOpen}
        closeModal={closeModal}
        openModal={openModal}
        trigger={triggerElement}
        actions={
          <>
            <Button title={i18next.t("Submit request")} color="blue" icon labelPosition="left" floated="right" {...submitButtonExtraProps}>
              <Icon name="paper plane" />
              {i18next.t("Submit")}
            </Button>
            <Button 
              title={i18next.t("Cancel request")} 
              onClick={() => confirmAction(() => onSubmit(() => sendRequest(request.links.actions.cancel, REQUEST_TYPE.CANCEL)), REQUEST_TYPE.CANCEL)} 
              negative icon labelPosition="left" floated="left"
            >
              <Icon name="trash alternate" />
              {i18next.t("Cancel request")}
            </Button>
            {formWillBeRendered && 
              <Button 
                title={i18next.t("Save drafted request")} 
                onClick={() => onSubmit(() => sendRequest(request.links.self, REQUEST_TYPE.SAVE))} 
                color="grey" icon labelPosition="left" floated="right"
              >
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