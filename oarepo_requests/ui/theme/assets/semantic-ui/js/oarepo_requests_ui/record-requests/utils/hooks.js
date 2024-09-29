import React, { useState, useCallback } from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button } from "semantic-ui-react";
import { useFormikContext } from "formik";
import { useMutation } from "@tanstack/react-query";
import { serializeCustomFields } from "../utils";
import {
  useConfirmModalContext,
  useRequestContext,
  useModalControlContext,
} from "../contexts";
import { REQUEST_TYPE } from "./objects";
import { http } from "@js/oarepo_ui";

/**
 * @typedef {import("semantic-ui-react").ConfirmProps} ConfirmProps
 */

export const useConfirmDialog = (isEventModal = false) => {
  const { setSubmitting } = useFormikContext();

  /** @type {[ConfirmProps, (props: ConfirmProps) => void]} */
  const [confirmDialogProps, setConfirmDialogProps] = useState({
    open: false,
    content: i18next.t("Are you sure?"),
    cancelButton: i18next.t("Close"),
    confirmButton: i18next.t("OK"),
    onCancel: () =>
      setConfirmDialogProps((props) => ({ ...props, open: false })),
    onConfirm: () =>
      setConfirmDialogProps((props) => ({ ...props, open: false })),
  });

  const confirmAction = useCallback(
    (onConfirm, requestType, createAndSubmit = false) => {
      /** @type {ConfirmProps} */
      let newConfirmDialogProps = {
        open: true,
        onConfirm: () => {
          setConfirmDialogProps((props) => ({ ...props, open: false }));
          onConfirm();
        },
        onCancel: () => {
          setConfirmDialogProps((props) => ({ ...props, open: false }));
          setSubmitting(false);
        },
      };

      switch (requestType) {
        case REQUEST_TYPE.CREATE:
          newConfirmDialogProps.header = isEventModal
            ? i18next.t("Submit event")
            : i18next.t("Create request");
          break;
        case REQUEST_TYPE.SUBMIT:
          newConfirmDialogProps.header = i18next.t("Submit request");
          newConfirmDialogProps.confirmButton = i18next.t("OK");
          break;
        case REQUEST_TYPE.CANCEL:
          newConfirmDialogProps.header = i18next.t("Cancel request");
          newConfirmDialogProps.confirmButton = (
            <Button negative>{i18next.t("Cancel request")}</Button>
          );
          break;
        case REQUEST_TYPE.ACCEPT:
          newConfirmDialogProps.header = i18next.t("Accept request");
          newConfirmDialogProps.confirmButton = (
            <Button positive>{i18next.t("Accept")}</Button>
          );
          break;
        case REQUEST_TYPE.DECLINE:
          newConfirmDialogProps.header = i18next.t("Decline request");
          newConfirmDialogProps.confirmButton = (
            <Button negative>{i18next.t("Decline")}</Button>
          );
          break;
        default:
          break;
      }

      if (createAndSubmit) {
        newConfirmDialogProps = {
          ...newConfirmDialogProps,
          header: i18next.t("Create and submit request"),
          confirmButton: (
            <Button positive>{i18next.t("Create and submit")}</Button>
          ),
          onConfirm: () => {
            setConfirmDialogProps((props) => ({ ...props, open: false }));
            onConfirm();
          },
        };
      }

      setConfirmDialogProps((props) => ({
        ...props,
        ...newConfirmDialogProps,
      }));
    },
    [setSubmitting, isEventModal]
  );

  return { confirmDialogProps, confirmAction };
};

export const useRequestsApi = (request) => {
  const { values: formValues, resetForm } = useFormikContext();
  const { confirmAction } = useConfirmModalContext();
  const mappedData = serializeCustomFields(formValues);

  const createAndSubmitRequest = useAction(async () => {
    const createdRequest = await http.post(
      request.links?.actions?.create,
      mappedData
    );
    const submittedRequest = await http.post(
      createdRequest.data?.links?.actions?.submit,
      mappedData
    );
    const redirectionURL = submittedRequest?.data?.links?.topic_html;
    if (redirectionURL && window.location.href !== redirectionURL) {
      window.location.href = redirectionURL;
    }
    resetForm();
  });

  const doCreateAndSubmitAction = (waitForConfirmation = false) => {
    if (waitForConfirmation) {
      confirmAction(createAndSubmitRequest.mutate(), REQUEST_TYPE.SUBMIT, true);
    } else {
      createAndSubmitRequest.mutate();
    }
  };

  const sendRequest = useAction(async (requestActionType) => {
    let response;
    const actionUrl = request.links?.actions[requestActionType];
    if (requestActionType === REQUEST_TYPE.SAVE) {
      response = await http.put(request.links?.self, mappedData);
    } else if (requestActionType === REQUEST_TYPE.ACCEPT) {
      response = await http.post(actionUrl);
    } else {
      response = await http.post(actionUrl, mappedData);
    }

    const redirectionURL = response?.data?.links?.topic_html;
    if (redirectionURL && window.location.href !== redirectionURL) {
      window.location.href = redirectionURL;
    }
    return response.data;
  });
  const doAction = async (requestActionType, waitForConfirmation = false) => {
    if (waitForConfirmation) {
      confirmAction(
        () => sendRequest.mutate(requestActionType),
        requestActionType
      );
    } else {
      sendRequest.mutate(requestActionType);
    }
  };

  return { doAction, doCreateAndSubmitAction };
};

const useAction = (action) => {
  const { onBeforeAction, onAfterAction, onActionError, fetchNewRequests } =
    useRequestContext();
  const modalControl = useModalControlContext();
  const { closeModal } = modalControl;
  const formik = useFormikContext();
  const { setFieldError, setSubmitting } = formik;
  return useMutation(
    async (requestActionType) => {
      if (onBeforeAction) {
        const shouldProceed = await onBeforeAction(formik, modalControl);
        if (!shouldProceed) {
          closeModal();
          return;
        }
      }
      return action(requestActionType);
    },
    {
      onError: (e, variables) => {
        if (onActionError) {
          onActionError(e, variables, formik, modalControl);
        } else {
          if (e?.response?.data?.errors) {
            setFieldError(
              "api",
              i18next.t(
                "The request could not be created due to validation errors. Please correct the errors and try again."
              )
            );
            setTimeout(() => {
              closeModal();
            }, 2500);
          } else {
            setFieldError(
              "api",
              i18next.t(
                "The action could not be executed. Please try again in a moment."
              )
            );
            setTimeout(() => {
              closeModal();
            }, 2500);
          }
        }
        setSubmitting(false);
      },
      onSuccess: (data, variables) => {
        if (onAfterAction) {
          onAfterAction(data, variables, formik, modalControl);
        }
        closeModal();
        fetchNewRequests();
        setSubmitting(false);
      },
      onMutate: () => {
        setSubmitting(true);
      },
    }
  );
};
