import React, { useRef, useEffect } from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Message, Form } from "semantic-ui-react";
import { useFormik, FormikProvider } from "formik";
// TODO: until we figure out a way to globally use sanitization with our hook
import {
  CommentPayloadSchema,
  RequestCommentInput,
} from "@js/oarepo_requests_common";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { http } from "@js/oarepo_ui";

export const EventSubmitForm = ({
  request,
  refetch,
  page,
  timelinePageSize,
}) => {
  const formik = useFormik({
    initialValues: {
      payload: {
        content: "",
        format: "html",
      },
    },
    onSubmit: () => {},
    validationSchema: CommentPayloadSchema,
    validateOnBlur: false,
    validateOnChange: false,
  });

  const { resetForm, values, setFieldError } = formik;
  const editorRef = useRef(null);
  const queryClient = useQueryClient();

  const { mutate, isError, isLoading, reset } = useMutation(
    () => http.post(request.links?.comments, values),
    {
      onSuccess: (response) => {
        if (response.status === 201) {
          queryClient.setQueryData(
            ["requestEvents", request.id, page],
            (oldData) => {
              if (!oldData) return;
              // a bit ugly, but it is a limitation of react query when data you recieve is nested
              const newData = [...oldData.data.hits.hits];
              if (oldData.data.hits.total + 1 > timelinePageSize) {
                newData.pop();
              }
              return {
                ...oldData,
                data: {
                  ...oldData.data,
                  hits: {
                    ...oldData.data.hits,
                    total: oldData.data.hits.total + 1,
                    hits: [response.data, ...newData],
                  },
                },
              };
            }
          );
        }
        setTimeout(() => refetch(), 1000);
        editorRef.current.setContent("");
        resetForm();
      },
      onError: (error) => {
        if (error.response?.data?.errors?.length > 0) {
          error.response.data.errors.forEach((error) => {
            setFieldError(error.field, error.messages[0]);
          });
        }
      },
    }
  );

  useEffect(() => {
    if (isError) {
      setTimeout(() => {
        reset();
        resetForm();
      }, 2500);
    }
    return () => isError && reset();
  }, [isError, reset, resetForm]);
  console.log(isError);
  return (
    <FormikProvider value={formik}>
      <Form className="ui form">
        <RequestCommentInput editorRef={editorRef} />
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
          color="blue"
          icon="send"
          type="button"
          loading={isLoading}
          disabled={isLoading}
          content={i18next.t("Leave comment")}
          onClick={() => mutate()}
        />
      </Form>
    </FormikProvider>
  );
};

EventSubmitForm.propTypes = {
  request: PropTypes.object,
  refetch: PropTypes.func,
  page: PropTypes.number,
  timelinePageSize: PropTypes.number,
};
