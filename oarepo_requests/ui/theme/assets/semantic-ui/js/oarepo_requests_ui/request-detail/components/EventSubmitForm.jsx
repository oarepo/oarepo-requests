import React, { useState, useRef } from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Message, FormField } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import axios from "axios";
import { RichEditor, RichInputField } from "react-invenio-forms";
import { Formik, Form } from "formik";

import { sanitizeInput } from "@js/oarepo_ui";
import { CommentPayloadSchema } from "../utils";

export const EventSubmitForm = ({ request, fetchEvents }) => {
  const [error, setError] = useState(null);
  
  const editorRef = useRef(null);

  const callApi = async (url, method = "POST", data = null) => {
    if (_isEmpty(url)) {
      console.log("URL parameter is missing or invalid.");
    }
    return axios({
      url: url,
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.inveniordm.v1+json'
      },
      data: data
  })};

  const onSubmit = async (values, { setSubmitting, resetForm }) => {
    setSubmitting(true);
    setError(null);
    try {
      await callApi(request.links?.comments, "POST", values);
    } catch (error) {
      setError(error);
    } finally {
      editorRef.current.setContent("");
      resetForm();
      fetchEvents();
      setSubmitting(false);
    }
  };

  return (
    <Formik
      initialValues={{ 
        payload: { 
          content: "",
          format: "html"
        }
      }}
      validationSchema={CommentPayloadSchema}
      onSubmit={onSubmit}
    >
      {({ values, isSubmitting, setFieldValue, setFieldTouched }) => (
        <Form>
          <FormField className={error ? "mt-25" : "mt-25 mb-25"}>
            <RichInputField
              fieldPath="payload.content"
              label={
                <label htmlFor="payload.content" hidden>{i18next.t("Comment")}</label>
              }
              optimized="true"
              placeholder={i18next.t('Your comment here...')}
              editor={
                <RichEditor
                  value={values.payload.content}
                  optimized
                  onFocus={(event, editor) => editorRef.current = editor}
                  onBlur={(event, editor) => {
                    const cleanedContent = sanitizeInput(editor.getContent());
                    setFieldValue("payload.content", cleanedContent);
                    setFieldTouched("payload.content", true);
                  }}
                />
              }
            />
          </FormField>
          {error && (
            <Message error>
              <Message.Header>{i18next.t("Error while submitting the comment")}</Message.Header>
              <p>{error?.message}</p>
            </Message>
          )}
          <Button
            floated="right"
            color="blue"
            icon="send"
            type="submit"
            loading={isSubmitting}
            disabled={isSubmitting}
            content={i18next.t("Comment")}
          />
        </Form>
      )}
    </Formik>
  );
}
