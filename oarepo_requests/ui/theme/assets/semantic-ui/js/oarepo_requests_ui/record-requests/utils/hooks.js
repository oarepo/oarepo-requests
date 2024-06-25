import React, { useState } from "react";

import _isEmpty from "lodash/isEmpty";
import axios from "axios";

import { isDeepEmpty } from "../utils";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button } from "semantic-ui-react";
import { useFormikContext } from "formik";

import { REQUEST_TYPE } from "./objects";

/** 
 * @typedef {import("semantic-ui-react").ConfirmProps} ConfirmProps
 */

export const useConfirmDialog = (formik, isEventModal = false) => {
  const { setSubmitting } = formik;

  /** @type {[ConfirmProps, (props: ConfirmProps) => void]} */
  const [confirmDialogProps, setConfirmDialogProps] = useState({
    open: false,
    content: i18next.t("Are you sure?"),
    cancelButton: i18next.t("Close"),
    confirmButton: i18next.t("OK"),
    onCancel: () => setConfirmDialogProps(props => ({ ...props, open: false })),
    onConfirm: () => setConfirmDialogProps(props => ({ ...props, open: false }))
  });

  const confirmAction = (onConfirm, requestType, createAndSubmit = false) => {
    /** @type {ConfirmProps} */
    let newConfirmDialogProps = {
      open: true,
      onConfirm: () => {
        setConfirmDialogProps(props => ({ ...props, open: false }));
        onConfirm(requestType);
      },
      onCancel: () => {
        setConfirmDialogProps(props => ({ ...props, open: false }));
        setSubmitting(false);
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
          onConfirm(requestType, true);
        }
      }
    }

    setConfirmDialogProps(props => ({ ...props, ...newConfirmDialogProps }));
  };

  return { confirmDialogProps, confirmAction };
}

export const useRequestsApi = () => {
  const {
    values: formValues,
    resetForm,
    submitForm,
    setSubmitting,
    setErrors,
  } = useFormikContext();

  const setError = error => { setErrors({ api: error }); };

  const callApi = async (url, method, data = formValues, doNotHandleResolve = false) => {
    if (_isEmpty(url)) {
      setError(new Error(i18next.t("Cannot send request. Please try again later.")));
      setSubmitting(false);
      return;
    }

    const request = axios({
      method: method,
      url: url,
      data: data,
      headers: { 'Content-Type': 'application/json' }
    });

    if (doNotHandleResolve) {
      return request;
    }

    return request
      .then(() => {
        resetForm();
      })
      .catch(error => {
        setError(error);
      });
  };

  const createAndSubmitRequest = async (actionUrl) => {
    try {
      const createdRequest = await callApi(actionUrl, 'post', formValues, true);
      await callApi(createdRequest.data?.links?.actions?.submit, 'post', {}, true);
      resetForm();
    } catch (error) {
      setError(error);
    }
  }

  const sendRequest = async (actionUrl, requestType, createAndSubmit = false) => {
    setSubmitting(true);
    setErrors({});
    if (createAndSubmit) {
      return createAndSubmitRequest();
    }
    if (requestType === REQUEST_TYPE.SAVE) {
      return callApi(actionUrl, 'put');
    } else if (requestType === REQUEST_TYPE.ACCEPT) { // Reload page after succesful "Accept" operation
      await callApi(actionUrl, 'post');
      window.location.reload();
      return;
    }
    const mappedData = !isDeepEmpty(formValues) ? {} : formValues;
    return callApi(actionUrl, 'post', mappedData);
  };

  return { sendRequest };
}