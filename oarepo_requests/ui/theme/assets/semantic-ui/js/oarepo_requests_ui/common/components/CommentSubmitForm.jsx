import React, { useEffect } from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Message, Form } from "semantic-ui-react";
import { useFormik, FormikProvider } from "formik";
import {
  CommentPayloadSchema,
  RequestCommentInput,
} from "@js/oarepo_requests_common";

export const CommentSubmitForm = ({ commentSubmitMutation }) => {
  const formik = useFormik({
    initialValues: {
      payload: {
        content: "",
        format: "html",
      },
    },
    validationSchema: CommentPayloadSchema,
    validateOnBlur: false,
    validateOnChange: false,
  });
  const {
    mutate: submitComment,
    isLoading,
    isError,
    reset: resetSendCommentMutation,
  } = commentSubmitMutation;
  const { resetForm, values, setFieldError } = formik;

  useEffect(() => {
    if (isError) {
      setTimeout(() => {
        resetSendCommentMutation();
        resetForm();
      }, 2500);
    }
    return () => isError && resetSendCommentMutation();
  }, [isError, resetSendCommentMutation, resetForm]);
  return (
    <FormikProvider value={formik}>
      <Form className="ui form">
        <RequestCommentInput />
        {isError && (
          <Message negative>
            <Message.Header>
              {i18next.t("Comment was not submitted successfully.")}
            </Message.Header>
          </Message>
        )}
        <Button
          size="tiny"
          floated="right"
          primary
          icon="send"
          type="button"
          labelPosition="left"
          loading={isLoading}
          disabled={isLoading}
          content={i18next.t("Leave comment")}
          onClick={() =>
            submitComment(values, {
              onSuccess: resetForm,
              onError: (error) => {
                if (error.response?.data?.errors?.length > 0) {
                  error.response.data.errors.forEach((error) => {
                    setFieldError(error.field, error.messages[0]);
                  });
                }
              },
            })
          }
        />
      </Form>
    </FormikProvider>
  );
};

CommentSubmitForm.propTypes = {
  commentSubmitMutation: PropTypes.object.isRequired,
};
