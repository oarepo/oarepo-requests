import React, { useState } from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button } from "semantic-ui-react";

import { REQUEST_TYPE } from "./objects";

/** 
 * @typedef {import("semantic-ui-react").ConfirmProps} ConfirmProps
 */

export const useConfirmDialog = (formik, sendRequest, isEventModal) => {
  /** @type {[ConfirmProps, (props: ConfirmProps) => void]} */
  const [confirmDialogProps, setConfirmDialogProps] = useState({
    open: false,
    content: i18next.t("Are you sure?"),
    cancelButton: i18next.t("Close"),
    confirmButton: i18next.t("OK"),
    onCancel: () => setConfirmDialogProps(props => ({ ...props, open: false })),
    onConfirm: () => setConfirmDialogProps(props => ({ ...props, open: false }))
  });

  const confirmAction = (requestType, createAndSubmit = false) => {
    /** @type {ConfirmProps} */
    let newConfirmDialogProps = {
      open: true,
      onConfirm: () => {
        setConfirmDialogProps(props => ({ ...props, open: false }));
        sendRequest(requestType);
      },
      onCancel: () => {
        setConfirmDialogProps(props => ({ ...props, open: false }));
        formik.setSubmitting(false);
      }
    };

    switch (requestType) {
      case REQUEST_TYPE.CREATE:
        newConfirmDialogProps.header = isEventModal ? i18next.t("Submit event") : i18next.t("Create request");
        break;
      case REQUEST_TYPE.SUBMIT:
        newConfirmDialogProps.header = i18next.t("Submit request");
        newConfirmDialogProps.confirmButton = i18next.t("OK");
        break;
      case REQUEST_TYPE.CANCEL:
        newConfirmDialogProps.header = i18next.t("Cancel request");
        newConfirmDialogProps.confirmButton = <Button negative>{i18next.t("Cancel request")}</Button>;
        break;
      case REQUEST_TYPE.ACCEPT:
        newConfirmDialogProps.header = i18next.t("Accept request");
        newConfirmDialogProps.confirmButton = <Button positive>{i18next.t("Accept")}</Button>;
        break;
      case REQUEST_TYPE.DECLINE:
        newConfirmDialogProps.header = i18next.t("Decline request");
        newConfirmDialogProps.confirmButton = <Button negative>{i18next.t("Decline")}</Button>;
        break;
      default:
        break;
    }

    if (createAndSubmit) {
      newConfirmDialogProps = {
        ...newConfirmDialogProps,
        header: i18next.t("Create and submit request"),
        confirmButton: <Button positive>{i18next.t("Create and submit")}</Button>,
        onConfirm: () => {
          setConfirmDialogProps(props => ({ ...props, open: false }));
          sendRequest(REQUEST_TYPE.CREATE, createAndSubmit);
        }
      }
    }

    setConfirmDialogProps(props => ({ ...props, ...newConfirmDialogProps }));
  };

  return { confirmDialogProps, confirmAction };
}
