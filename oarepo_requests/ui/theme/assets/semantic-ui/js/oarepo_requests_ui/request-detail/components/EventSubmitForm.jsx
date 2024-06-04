import React, { useState, useEffect, useRef } from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Grid, List, Divider, Comment, Header, Container, Icon, Menu, Message, Feed, Dimmer, Loader, Placeholder, Segment, FormField } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import _sortBy from "lodash/sortBy";
import axios from "axios";
import { RichEditor } from "react-invenio-forms";
import { RichInputField } from "@js/oarepo_ui";

import { Formik, Field, Form, ErrorMessage } from "formik";
import * as Yup from 'yup';
import { sanitizeHtml } from "sanitize-html";

import { ReadOnlyCustomFields } from "@js/oarepo_requests/components";
import { SideRequestInfo } from ".";

const sanitizeInput = (htmlString, validTags) => {
  const decodedString = decode(htmlString);
  const cleanInput = sanitizeHtml(decodedString, {
    allowedTags: validTags || ["b", "i", "em", "strong", "a", "div", "li", "p"],
    allowedAttributes: {
      a: ["href"],
    },
  });
  return cleanInput;
};

export const EventSubmitForm = ({ request }) => {
  const [error, setError] = useState(null);

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

  const onSubmit = async (values, { setSubmitting }) => {
    setSubmitting(true);
    setError(null);
    try {
      console.log("Sending request");
      await callApi(request.links?.comments, "POST", values);
    } catch (error) {
      setError(error);
    } finally {
      setSubmitting(false);
    }
  }

  const CommentPayloadSchema = Yup.object().shape({
    payload: Yup.object().shape({
      content: Yup.string()
        .min(1, i18next.t("Comment must be at least 1 character long.")),
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
          <Field name="payload.content">
            {({ field }) => (
              <FormField className={error ? "mt-25" : "mt-25 mb-25"}>
                <label htmlFor={field.id || field.name} hidden>{i18next.t("Comment")}</label>
                <RichEditor
                  value={values.payload.content}
                  optimized
                  onBlur={(event, editor) => {
                    // const cleanedContent = sanitizeInput(
                    //   editor.getContent(),
                    //   null
                    // );
                    console.log(event, editor);
                    const cleanedContent = editor.getContent();
                    console.log(cleanedContent);
                    setFieldValue("payload.content", cleanedContent);
                    setFieldTouched("payload.content", true);
                  }}
                  {...field}
                />
                <ErrorMessage name="payload.content" render={(message) => <Message error attached="bottom">{message}</Message>} />
              </FormField>
            )}
          </Field>
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
