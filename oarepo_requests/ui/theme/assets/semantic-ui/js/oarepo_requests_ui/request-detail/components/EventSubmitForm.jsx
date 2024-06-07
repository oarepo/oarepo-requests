import React, { useState, useEffect, useRef } from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Grid, List, Divider, Comment, Header, Container, Icon, Menu, Message, Feed, Dimmer, Loader, Placeholder, Segment, FormField } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import _sortBy from "lodash/sortBy";
import axios from "axios";
import { RichEditor, FieldLabel, RichInputField } from "react-invenio-forms";

import { Formik, Field, Form, ErrorMessage } from "formik";
import * as Yup from 'yup';

import { ReadOnlyCustomFields } from "@js/oarepo_requests/components";
import { SideRequestInfo } from ".";
import { sanitizeInput } from "../utils";

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
        'Accept': 'application/json'
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
  }

  const CommentPayloadSchema = Yup.object().shape({
    payload: Yup.object().shape({
      content: Yup.string()
        .min(1, i18next.t("Comment must be at least 1 character long."))
        .required(i18next.t("Comment must be at least 1 character long.")),
      format: Yup.string().equals(["html"], i18next.t("Invalid format."))
    })
  });

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
