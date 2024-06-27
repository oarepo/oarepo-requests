import React from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon, Confirm } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import { useFormikContext } from "formik";
import { useConfirmationModal } from "@js/oarepo_ui";

import { NewRequestModal, CreateRequestModalContent } from "..";
import { REQUEST_TYPE } from "../../utils/objects";
import { useRequestsApi, useConfirmDialog } from "../../utils/hooks";

export const CreateModal = ({ requestType, fetchNewRequests, triggerElement }) => {
  const { 
    isOpen: isModalOpen, 
    close: closeModal,
    open: openModal
  } = useConfirmationModal();
  const { sendRequest, createAndSubmitRequest } = useRequestsApi();
  const { confirmDialogProps, confirmAction } = useConfirmDialog();
  const { setSubmitting, submitForm, setErrors } = useFormikContext();

  const onSubmit = async (submitEvent) => {
    try {
      await submitEvent();
      closeModal();
      fetchNewRequests();
    } catch (e) { /* empty */ }
  };

  const customSubmitHandler = async (submitButtonName) => {
    try {
      await submitForm();
      if (submitButtonName === "create-and-submit-request") {
        !_isEmpty(requestType?.payload_ui) ? 
          confirmAction(() => onSubmit(() => createAndSubmitRequest(requestType.links.actions.create)), REQUEST_TYPE.SUBMIT, true) : 
          onSubmit(() => createAndSubmitRequest(requestType.links.actions.create));
        return;
      }
      onSubmit(() => sendRequest(requestType.links.actions.create, REQUEST_TYPE.CREATE));
    } catch (error) {
      setErrors({ api: error });
    } finally {
      setSubmitting(false);
    }
  };

  const requestModalHeader = !_isEmpty(requestType?.title) ? requestType.title : (!_isEmpty(requestType?.name) ? requestType.name : requestType.type);

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
            {requestType?.payload_ui &&
              <Button type="submit" form="request-form" name="create-request" title={i18next.t("Create request")} color="blue" icon labelPosition="left" floated="right">
                <Icon name="plus" />
                {i18next.t("Create")}
              </Button>
            }
            <Button type="submit" form="request-form" name="create-and-submit-request" title={i18next.t("Submit request")} color="blue" icon labelPosition="left" floated="right">
              <Icon name="paper plane" />
              {i18next.t("Submit")}
            </Button>
          </>
        }
        content={
          <CreateRequestModalContent requestType={requestType} customSubmitHandler={customSubmitHandler} />
        }
      />
      <Confirm {...confirmDialogProps} />
    </>
  );
}