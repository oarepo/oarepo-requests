import React, { useState, useCallback } from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button } from "semantic-ui-react";
import { useFormikContext } from "formik";

import { isDeepEmpty } from "../utils";
import { useConfirmModalContext } from "../contexts";
import { REQUEST_TYPE } from "./objects";
import { http } from "react-invenio-forms";

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

export const useRequestsApi = (request, onSubmit) => {
  const { values: formValues, resetForm } = useFormikContext();
  const { confirmAction } = useConfirmModalContext();

  const createAndSubmitRequest = () => {
    onSubmit(
      async () => {
        const createdRequest = await http.post(
          request.links?.actions?.create,
          formValues
        );
        await http.post(createdRequest.data?.links?.actions?.submit, {});
        resetForm();
      },
      undefined,
      REQUEST_TYPE.CREATE
    );
  };

  const doCreateAndSubmitAction = (waitForConfirmation = false) => {
    if (waitForConfirmation) {
      confirmAction(createAndSubmitRequest, REQUEST_TYPE.SUBMIT, true);
    } else {
      createAndSubmitRequest();
    }
  };

  const sendRequest = async (actionUrl, requestActionType) => {
    let response;
    if (requestActionType === REQUEST_TYPE.SAVE) {
      response = await http.put(actionUrl);
    } else if (requestActionType === REQUEST_TYPE.ACCEPT) {
      // Reload page after succesful "Accept" operation
      response = await http.post(actionUrl);
      // window.location.reload();
    } else {
      const mappedData = isDeepEmpty(formValues) ? {} : formValues;
      response = await http.post(actionUrl, mappedData);
    }
    if (response?.payload?.redirectUrl) {
      window.location.href = response.payload.redirectUrl;
    }
    return response;
  };

  const doAction = async (requestActionType, waitForConfirmation = false) => {
    const actionUrl = request.links.actions[requestActionType];
    if (waitForConfirmation) {
      confirmAction(
        () =>
          onSubmit(
            async () => sendRequest(actionUrl, requestActionType),
            undefined,
            requestActionType
          ),
        requestActionType
      );
    } else {
      onSubmit(
        async () => sendRequest(actionUrl, requestActionType),
        undefined,
        requestActionType
      );
    }
  };

  return { doAction, doCreateAndSubmitAction };
};
