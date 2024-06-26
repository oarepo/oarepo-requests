import React, { useEffect, useRef } from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Dimmer, Loader, Modal, Button, Icon, Message } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import { useFormikContext } from "formik";

/** 
 * @typedef {import("../types").Request} Request
 * @typedef {import("../types").RequestType} RequestType
 * @typedef {import("../types").RequestTypeEnum} RequestTypeEnum
 * @typedef {import("react").ReactElement} ReactElement
 * @typedef {import("semantic-ui-react").ConfirmProps} ConfirmProps
 */

/** @param {{ header: string | ReactElement, requestType: RequestType, trigger: ReactElement, actions: ReactElement, content: ReactElement }} props */
export const NewRequestModal = ({ header, isOpen, closeModal, openModal, trigger, actions, content }) => {
  const errorMessageRef = useRef(null);
  const {
    isSubmitting,
    resetForm,
    setErrors,
    errors,
  } = useFormikContext();

  const error = errors?.api;

  useEffect(() => {
    if (error) {
      errorMessageRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [error]);

  const onClose = () => {
    closeModal();
    setErrors({});
    resetForm();
  };

  return (
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
        {content}
      </Modal.Content>
      <Modal.Actions>
        {actions}
        <Button onClick={onClose} icon labelPosition="left">
          <Icon name="cancel" />
          {i18next.t("Close")}
        </Button>
      </Modal.Actions>
    </Modal>
  );
};
