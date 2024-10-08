import React, { useRef } from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Message, FormField, Form } from "semantic-ui-react";
import { RichEditor, RichInputField } from "react-invenio-forms";
import { useFormik, FormikProvider } from "formik";
// TODO: until we figure out a way to globally use sanitization with our hook
import sanitizeHtml from "sanitize-html";
import { CommentPayloadSchema } from "../utils";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { http } from "@js/oarepo_ui";
import { CodeGen } from "ajv";

export const EventSubmitForm = ({ request }) => {
  const formik = useFormik({
    initialValues: {
      payload: {
        content: "",
        format: "html",
      },
    },
    onSubmit: () => {},
    validationSchema: CommentPayloadSchema,
  });

  const { resetForm, setFieldValue, setFieldTouched, values, setFieldError } =
    formik;
  const editorRef = useRef(null);
  const queryClient = useQueryClient();

  const { mutate, error, isLoading } = useMutation(
    () => http.post(request.links?.comments, values),
    {
      onSuccess: (response) => {
        if (response.status === 201) {
          queryClient.setQueryData(["requestEvents"], (oldData) => {
            if (!oldData) return;
            return {
              ...oldData,
              data: {
                ...oldData.data,
                hits: {
                  ...oldData.data.hits,
                  hits: [...oldData.data.hits.hits, response.data],
                },
              },
            };
          });
        }
      },
      onError: (error) => {
        console.log(error.response);
        if (error.response?.data?.errors?.length > 0) {
          error.response.data.errors.forEach((error) => {
            console.log(error);
            setFieldError(error.field, error.messages[0]);
          });
        }
      },
      onSettled: () => {
        editorRef.current.setContent("");
        resetForm();
      },
    }
  );
  return (
    <FormikProvider value={formik}>
      <Form className="ui form">
        <FormField>
          <RichInputField
            fieldPath="payload.content"
            label={
              <label htmlFor="payload.content" hidden>
                {i18next.t("Comment")}
              </label>
            }
            optimized="true"
            placeholder={i18next.t("Your comment here...")}
            editor={
              <RichEditor
                initialValue={values.payload.content}
                inputValue={() => values.payload.content}
                optimized
                onFocus={(event, editor) => (editorRef.current = editor)}
                onBlur={(event, editor) => {
                  const cleanedContent = sanitizeHtml(editor.getContent());
                  setFieldValue("payload.content", cleanedContent);
                  setFieldTouched("payload.content", true);
                }}
              />
            }
          />
        </FormField>
        {error && (
          <Message negative>
            <Message.Header>
              {i18next.t("Error while submitting the comment")}
            </Message.Header>
          </Message>
        )}
        <Button
          floated="right"
          color="blue"
          icon="send"
          type="button"
          loading={isLoading}
          disabled={isLoading}
          content={i18next.t("Comment")}
          onClick={() => mutate()}
        />
      </Form>
    </FormikProvider>
  );
};

EventSubmitForm.propTypes = {
  request: PropTypes.object,
  setEvents: PropTypes.func,
};
