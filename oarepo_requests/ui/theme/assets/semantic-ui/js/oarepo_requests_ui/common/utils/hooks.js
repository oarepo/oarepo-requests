import React, { useState, useCallback } from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button } from "semantic-ui-react";
import { useMutation } from "@tanstack/react-query";
import {
  useCallbackContext,
  REQUEST_TYPE,
  WarningMessage,
  RequestCommentInput,
} from "@js/oarepo_requests_common";
import { useFormikContext } from "formik";

/**
 * @typedef {import("semantic-ui-react").ConfirmProps} ConfirmProps
 */

export const useConfirmDialog = (requestOrRequestType) => {
  /** @type {[ConfirmProps, (props: ConfirmProps) => void]} */
  const formik = useFormikContext();
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
    (onConfirm, requestActionType, extraData) => {
      const dangerous = extraData?.dangerous;
      /** @type {ConfirmProps} */
      let newConfirmDialogProps = {
        open: true,
        header: `${i18next.t("Are you sure you wish to")} ${
          requestOrRequestType.name
        }`,
        content: dangerous ? <WarningMessage /> : i18next.t("Are you sure?"),
        onConfirm: () => {
          setConfirmDialogProps((props) => ({ ...props, open: false }));
          onConfirm();
        },
        onCancel: () => {
          setConfirmDialogProps((props) => ({ ...props, open: false }));
          formik?.resetForm();
        },
      };
      switch (requestActionType) {
        case REQUEST_TYPE.CREATE:
          newConfirmDialogProps.header = `${i18next.t("Create request")} (${
            requestOrRequestType.name
          })`;

          if (dangerous) {
            newConfirmDialogProps.confirmButton = (
              <Button negative content={i18next.t("Proceed")} />
            );
            newConfirmDialogProps.content = (
              <WarningMessage
                message={i18next.t(
                  "Are you sure you wish to proceed? After this request is accepted, it will not be possible to reverse the action."
                )}
              />
            );
          }

          break;
        case REQUEST_TYPE.SUBMIT:
          newConfirmDialogProps.header = `${i18next.t("Submit request")} (${
            requestOrRequestType.name
          })`;

          if (dangerous) {
            newConfirmDialogProps.confirmButton = (
              <Button negative content={i18next.t("Proceed")} />
            );
            newConfirmDialogProps.content = (
              <WarningMessage
                message={i18next.t(
                  "Are you sure you wish to proceed? After this request is accepted, it will not be possible to reverse the action."
                )}
              />
            );
          }
          break;
        case REQUEST_TYPE.CANCEL:
          newConfirmDialogProps.header = `${i18next.t("Cancel request")} (${
            requestOrRequestType.name
          })`;
          newConfirmDialogProps.confirmButton = (
            <Button negative>{i18next.t("Cancel request")}</Button>
          );
          break;
        case REQUEST_TYPE.ACCEPT:
          newConfirmDialogProps.header = `${i18next.t("Accept request")} (${
            requestOrRequestType.name
          })`;
          newConfirmDialogProps.confirmButton = (
            <Button positive={!dangerous} negative={dangerous}>
              {i18next.t("Accept")}
            </Button>
          );
          newConfirmDialogProps.content = (
            <React.Fragment>
              {dangerous && (
                <WarningMessage
                  message={
                    "This action is irreversible. Are you sure you wish to accept this request?"
                  }
                />
              )}
            </React.Fragment>
          );
          break;
        case REQUEST_TYPE.DECLINE:
          newConfirmDialogProps.header = `${i18next.t("Decline request")} (${
            requestOrRequestType.name
          })`;
          newConfirmDialogProps.confirmButton = (
            <Button negative>{i18next.t("Decline")}</Button>
          );
          newConfirmDialogProps.content = (
            <div className="content">
              <RequestCommentInput />
            </div>
          );
          break;
        default:
          break;
      }
      setConfirmDialogProps((props) => ({
        ...props,
        ...newConfirmDialogProps,
      }));
    },
    []
  );

  return { confirmDialogProps, confirmAction };
};

export const useAction = ({
  action,
  requestOrRequestType,
  formik,
  modalControl,
} = {}) => {
  const { onBeforeAction, onAfterAction, onActionError, fetchNewRequests } =
    useCallbackContext();
  return useMutation(
    async () => {
      formik?.setSubmitting(true);
      if (onBeforeAction) {
        const shouldProceed = await onBeforeAction(formik, modalControl);
        if (!shouldProceed) {
          modalControl?.closeModal();
          return;
        }
      }

      return action(requestOrRequestType, formik?.values);
    },
    {
      onError: (e, variables) => {
        formik?.setSubmitting(false);

        if (onActionError) {
          onActionError(e, variables, formik, modalControl);
        } else {
          if (e?.response?.data?.errors) {
            formik?.setFieldError(
              "api",
              i18next.t(
                "The request could not be created due to validation errors. Please correct the errors and try again."
              )
            );
            setTimeout(() => {
              modalControl?.closeModal();
            }, 2500);
          } else {
            formik?.setFieldError(
              "api",
              i18next.t(
                "The action could not be executed. Please try again in a moment."
              )
            );
            setTimeout(() => {
              modalControl?.closeModal();
            }, 2500);
          }
        }
      },
      onSuccess: (data, variables) => {
        formik?.setSubmitting(false);
        if (onAfterAction) {
          onAfterAction(data, variables, formik, modalControl);
        }
        const redirectionURL = data?.data?.links?.topic_html;
        modalControl?.closeModal();
        fetchNewRequests?.();

        if (redirectionURL) {
          window.location.href = redirectionURL;
        }
      },
    }
  );
};
