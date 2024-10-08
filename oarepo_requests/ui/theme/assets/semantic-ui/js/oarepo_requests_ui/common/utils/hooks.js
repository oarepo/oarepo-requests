import React, { useState, useCallback } from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button } from "semantic-ui-react";
import { useMutation } from "@tanstack/react-query";
import {
  useRequestContext,
  REQUEST_TYPE,
  WarningMessage,
  RequestCommentInput,
} from "@js/oarepo_requests_common";

/**
 * @typedef {import("semantic-ui-react").ConfirmProps} ConfirmProps
 */

export const useConfirmDialog = (isEventModal = false) => {
  /** @type {[ConfirmProps, (props: ConfirmProps) => void]} */

  const initialState = {
    open: false,
    content: i18next.t("Are you sure?"),
    cancelButton: i18next.t("Close"),
    confirmButton: i18next.t("OK"),
    onCancel: () =>
      setConfirmDialogProps((props) => ({ ...props, open: false })),
    onConfirm: () =>
      setConfirmDialogProps((props) => ({ ...props, open: false })),
  };
  const [confirmDialogProps, setConfirmDialogProps] = useState(initialState);

  const confirmAction = useCallback(
    (onConfirm, requestActionType, { dangerous, hasForm, editable } = {}) => {
      /** @type {ConfirmProps} */
      let newConfirmDialogProps = {
        open: true,
        content: dangerous ? <WarningMessage /> : i18next.t("Are you sure?"),
        onConfirm: () => {
          setConfirmDialogProps((props) => ({ ...props, open: false }));
          onConfirm();
        },
        onCancel: () => {
          setConfirmDialogProps(initialState);
        },
      };

      switch (requestActionType) {
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
          newConfirmDialogProps.content = (
            <div className="content">
              <RequestCommentInput />
            </div>
          );
          break;
        case REQUEST_TYPE.ACCEPT:
          newConfirmDialogProps.header = i18next.t("Accept request");
          newConfirmDialogProps.confirmButton = (
            <Button positive>{i18next.t("Accept")}</Button>
          );
          newConfirmDialogProps.content = (
            <div className="content">
              <RequestCommentInput />
            </div>
          );
          break;
        case REQUEST_TYPE.DECLINE:
          newConfirmDialogProps.header = i18next.t("Decline request");
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

      // if (createAndSubmit) {
      //   newConfirmDialogProps = {
      //     ...newConfirmDialogProps,
      //     header: i18next.t("Create and submit request"),
      //     confirmButton: (
      //       <Button positive>{i18next.t("Create and submit")}</Button>
      //     ),
      //     onConfirm: () => {
      //       setConfirmDialogProps((props) => ({ ...props, open: false }));
      //       onConfirm();
      //     },
      //   };
      // }

      setConfirmDialogProps((props) => ({
        ...props,
        ...newConfirmDialogProps,
      }));
    },
    [isEventModal]
  );

  return { confirmDialogProps, confirmAction };
};

export const useAction = ({
  action,
  requestOrRequestType,
  formik,
  modalControl,
} = {}) => {
  const {
    onBeforeAction = undefined,
    onAfterAction = undefined,
    onActionError = undefined,
    fetchNewRequests = undefined,
  } = useRequestContext() || {};
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
              formik?.setSubmitting(false);
            }, 2500);
          }
        }
      },
      onSuccess: (data, variables) => {
        if (onAfterAction) {
          onAfterAction(data, variables, formik, modalControl);
        }
        const redirectionURL = data?.data?.links?.topic_html;

        formik?.setSubmitting(false);
        modalControl?.closeModal();
        fetchNewRequests?.();

        if (redirectionURL) {
          window.location.href = redirectionURL;
        }
      },
    }
  );
};
