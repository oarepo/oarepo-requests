import React, { useState } from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Dimmer, Loader, Modal, Button, Icon, Message, FormField } from "semantic-ui-react";
import {
  RichEditor,
  FieldLabel,
  RichInputField,
} from "react-invenio-forms";
import { Formik, Form } from "formik";

import { sanitizeInput } from "@js/oarepo_ui";

/** @param {{ request: import("../types").Request, requestModalHeader: string, handleSubmit: (v) => Promise, triggerButton: ReactElement, submitButton: ReactElement }} props */
export const ConfirmModal = ({ request, requestModalHeader, handleSubmit, triggerButton, submitButton }) => {
  const [modalOpen, setModalOpen] = useState(false);
  const [error, setError] = useState(null);

  const onClose = () => {
    setModalOpen(false);
    setError(null);
  };

  const onSubmit = async (values, { setSubmitting }) => {
    setError(null);
    try {
      await handleSubmit(values);
      location.reload();
    } catch (error) {
      setError(error);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      className="requests-request-modal"
      as={Dimmer.Dimmable}
      blurring
      onClose={onClose}
      onOpen={() => setModalOpen(true)}
      open={modalOpen}
      trigger={triggerButton || <Button content="Open Modal" />}
      closeOnDocumentClick={false}
      closeOnDimmerClick={false}
      role="dialog"
      aria-labelledby="request-modal-header"
    >
      <Formik 
        initialValues={{ 
          payload: { 
            content: "",
            format: "html"
          }
        }}
        onSubmit={onSubmit}
      >
        {({ isSubmitting, values, setFieldValue, setFieldTouched }) => (
          <>
            <Dimmer active={isSubmitting}>
              <Loader inverted size="large" />
            </Dimmer>
            <Modal.Header as="h2" id="request-modal-header">{requestModalHeader ?? request?.type}</Modal.Header>
            <Modal.Content>
              {error && (
                <Message error>
                  <Message.Header>{i18next.t("Error while submitting comment.")}</Message.Header>
                  <p>{error?.message}</p>
                </Message>
              )}
              <Form id="submit-request-form">
                <FormField>
                  <RichInputField
                    fieldPath="payload.content"
                    label={
                      <FieldLabel htmlFor="payload.content" label={`${i18next.t("Add comment")} (${i18next.t("optional")})`} className="rel-mb-25" />
                    }
                    optimized="true"
                    placeholder={i18next.t('Your comment here...')}
                    editor={
                      <RichEditor
                        value={values.payload.content}
                        optimized
                        onBlur={(event, editor) => {
                          const cleanedContent = sanitizeInput(editor.getContent());
                          setFieldValue("payload.content", cleanedContent);
                          setFieldTouched("payload.content", true);
                        }}
                      />
                    }
                  />
                </FormField>
              </Form>
            </Modal.Content>
            <Modal.Actions>
              <Button onClick={onClose} icon compact labelPosition="left" floated="left">
                <Icon name="cancel" />
                {i18next.t("Cancel")}
              </Button>
              {submitButton ?? React.cloneElement(triggerButton, { type: "submit", form: "submit-request-form" })}
            </Modal.Actions>
          </>
        )}
      </Formik>
    </Modal>
  );
};

ConfirmModal.propTypes = {
  request: PropTypes.object.isRequired,
  requestModalHeader: PropTypes.string,
  handleSubmit: PropTypes.func,
  triggerButton: PropTypes.element,
  submitButton: PropTypes.element,
};