import React from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon, Confirm } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import { useFormikContext } from "formik";

import { RequestModal, CreateRequestModalContent } from "..";
import { REQUEST_TYPE } from "../../utils/objects";
import { useRequestsApi, useConfirmDialog, useRequestModal } from "../../utils/hooks";
import { useRequestContext } from "../../contexts";

export const CreateEventModal = ({ eventType, triggerElement }) => {
  const { fetchNewRequests } = useRequestContext();
  const {
    isOpen: isModalOpen,
    close: closeModal,
    open: openModal,
    onSubmit
  } = useRequestModal(fetchNewRequests);
  const { sendRequest } = useRequestsApi();
  const { confirmDialogProps } = useConfirmDialog(true);
  const { setSubmitting, submitForm, setErrors } = useFormikContext();

  const customSubmitHandler = async () => {
    const actionUrl = eventType.links?.actions.create ?? eventType.links?.create;
    try {
      await submitForm();
      onSubmit(() => sendRequest(actionUrl, REQUEST_TYPE.CREATE));
    } catch (error) {
      setErrors({ api: error });
    } finally {
      setSubmitting(false);
    }
  };

  const requestModalHeader = !_isEmpty(eventType?.title) ? eventType.title : (!_isEmpty(eventType?.name) ? eventType.name : eventType.type);

  return (
    <>
      <RequestModal
        header={requestModalHeader}
        isOpen={isModalOpen}
        closeModal={closeModal}
        openModal={openModal}
        trigger={triggerElement}
        actions={
          <Button type="submit" form="request-form" title={i18next.t("Submit")} color="blue" icon labelPosition="left" floated="right">
            <Icon name="plus" />
            {i18next.t("Submit")}
          </Button>
        }
        content={
          <CreateRequestModalContent requestType={eventType} customSubmitHandler={customSubmitHandler} />
        }
      />
      <Confirm {...confirmDialogProps} />
    </>
  );
}