import React, { useState, useEffect, useRef } from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Dimmer, Loader, Modal, Button, Icon, Message, Divider, FormTextArea, FormField } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import _isFunction from "lodash/isFunction";
import {
  RichEditor,
} from "react-invenio-forms";
import { sanitizeInput } from "@js/oarepo_ui";

import { Formik, Field, Form, ErrorMessage } from "formik";
import * as Yup from 'yup';
import { delay } from "bluebird";

/** 
 * @typedef {import("../types").Request} Request
 * @typedef {import("../types").RequestType} RequestType
 * @typedef {import("../types").RequestTypeEnum} RequestTypeEnum
 * @typedef {import("react").ReactElement} ReactElement
 * @typedef {import("semantic-ui-react").ConfirmProps} ConfirmProps
 */

/** @param {{ request: Request, requestModalHeader: string, handleSubmit: (v) => Promise, triggerButton: ReactElement, submitButton: ReactElement }} props */
export const ConfirmModal = ({ request, requestModalHeader, handleSubmit, triggerButton, submitButton }) => {
  const [modalOpen, setModalOpen] = useState(false);
  const [error, setError] = useState(null);

  const errorMessageRef = useRef(null);

  useEffect(() => {
    if (error) {
      errorMessageRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [error]);

  const onClose = () => {
    setModalOpen(false);
    setError(null);
  };

  const onSubmit = async (values, { setSubmitting }) => {
    try {
      console.log("Sending request");
      await delay(1000);
      _isFunction(handleSubmit) && await handleSubmit(values);
    } catch (error) {
      setError(error);
    } finally {
      setSubmitting(false);
    }
  }

  const PayloadSchema = Yup.object().shape({
    payload: Yup.object().shape({
      content: Yup.string()
      .min(1, i18next.t("Comment must be at least 1 character long."))
    })
  });

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
          "payload": {
            "content": "" 
          }
        }} 
        validationSchema={PayloadSchema}
        onSubmit={onSubmit}
      >
        {({ isSubmitting, values, setFieldValue, setFieldTouched }) => (
          <>
            <Dimmer active={isSubmitting}>
              <Loader inverted size="large" />
            </Dimmer>
            <Modal.Header as="h2" id="request-modal-header">{requestModalHeader ?? request?.type}</Modal.Header>
            <Modal.Content>
              {error &&
                <Message ref={errorMessageRef} negative>
                  <Message.Header>{i18next.t("Error")}</Message.Header>
                  <p>{error?.message}</p>
                </Message>
              }
              <Form id="submit-request-form">
                <Field name="payload.content">
                  {({ field }) => (
                    <FormField>
                      <label htmlFor={field.id || field.name}>{`${i18next.t("Add comment")} (${i18next.t("optional")})`}</label>
                      <Divider hidden />
                      <RichEditor
                        value={values.payload.content}
                        optimized
                        onBlur={(event, editor) => {
                          const cleanedContent = sanitizeInput(
                            editor.getContent(),
                            null
                          );
                          setFieldValue("payload.content", cleanedContent);
                          setFieldTouched("payload.content", true);
                        }}
                        {...field}
                      />
                    </FormField>
                  )}
                </Field>
                <ErrorMessage name="payload.content" render={(message) => <Message negative attached="bottom">{message}</Message>} />
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