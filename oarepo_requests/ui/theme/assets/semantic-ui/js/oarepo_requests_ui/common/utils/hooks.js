import React, { useState, useCallback } from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Message, Icon } from "semantic-ui-react";
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

const ConfirmationModalConfirmButton = (uiProps) => (
  <Button
    className="requests confirmation-modal-confirm-button"
    content={i18next.t("OK")}
    {...uiProps}
  />
);

const ConfirmationModalCancelButton = (uiProps) => (
  <Button
    content={i18next.t("Cancel")}
    className="requests confirmation-modal-cancel-button"
    {...uiProps}
  />
);
export const useConfirmDialog = (requestOrRequestType) => {
  /** @type {[ConfirmProps, (props: ConfirmProps) => void]} */
  const formik = useFormikContext();
  const [confirmDialogProps, setConfirmDialogProps] = useState({
    open: false,
    content: i18next.t("Are you sure?"),
    cancelButton: <ConfirmationModalCancelButton />,
    confirmButton: <ConfirmationModalConfirmButton />,
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
              <ConfirmationModalConfirmButton
                negative
                content={i18next.t("Proceed")}
              />
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
              <ConfirmationModalConfirmButton
                negative
                content={i18next.t("Proceed")}
              />
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
            <ConfirmationModalConfirmButton
              content={i18next.t("Cancel request")}
              negative
            />
          );
          break;
        case REQUEST_TYPE.ACCEPT:
          newConfirmDialogProps.header = `${i18next.t("Accept request")} (${
            requestOrRequestType.name
          })`;
          newConfirmDialogProps.confirmButton = (
            <ConfirmationModalConfirmButton
              positive={!dangerous}
              negative={dangerous}
              content={i18next.t("Accept")}
            />
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
            <ConfirmationModalConfirmButton
              content={i18next.t("Decline")}
              negative
            />
          );
          newConfirmDialogProps.content = (
            <div className="content">
              <RequestCommentInput
                label={`${i18next.t("Add comment")} (${i18next.t("optional")})`}
              />
              <Message>
                <Icon name="info circle" className="text size large" />
                <span>
                  {i18next.t(
                    "It is highly recommended to provide an explanation for the rejection of the request. Note that it is always possible to provide explanation later on the request timeline."
                  )}
                </span>
              </Message>
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
  const { onBeforeAction, onAfterAction, onActionError } = useCallbackContext();
  return useMutation(
    async () => {
      if (onBeforeAction) {
        const shouldProceed = await onBeforeAction(formik, modalControl);
        if (!shouldProceed) {
          modalControl?.closeModal();
          throw new Error("Could not proceed with the action.");
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
            }, 2500);
          }
        }
      },
      onSuccess: (data, variables) => {
        if (onAfterAction) {
          onAfterAction(data, variables, formik, modalControl);
        }
        const redirectionURL = data?.data?.links?.topic_html;
        modalControl?.closeModal();

        if (redirectionURL) {
          window.location.href = redirectionURL;
        } else {
          // TODO: some requests after they complete no longer have a topic_html,
          // so redirecting to dashboard instead
          window.location.href = "/me/records/";
          // fetchNewRequests?.();
        }
      },
    }
  );
};
