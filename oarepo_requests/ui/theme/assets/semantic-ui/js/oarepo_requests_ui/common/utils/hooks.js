/*
 * Copyright (C) 2024 CESNET z.s.p.o.
 *
 * oarepo-requests is free software; you can redistribute it and/or
 * modify it under the terms of the MIT License; see LICENSE file for more
 * details.
 */
import { useMutation } from "@tanstack/react-query";
import { useCallbackContext } from "@js/oarepo_requests_common";
import {
  cfValidationErrorPlugin,
  recordValidationErrorsPlugin,
  defaultErrorHandlingPlugin,
} from "./error-plugins";

export const useAction = ({
  action,
  requestOrRequestType,
  formik,
  modalControl,
  requestActionName,
} = {}) => {
  const {
    onBeforeAction,
    onAfterAction,
    onErrorPlugins = [],
    actionExtraContext,
  } = useCallbackContext();
  const handleActionError = (e, variables) => {
    const context = {
      e,
      variables,
      formik,
      modalControl,
      requestOrRequestType,
      requestActionName,
      actionExtraContext,
    };

    for (const plugin of onErrorPlugins) {
      const handled = plugin(e, context);
      if (handled) {
        return;
      }
    }

    const defaultPlugins = [
      cfValidationErrorPlugin,
      recordValidationErrorsPlugin,
    ];

    for (const plugin of defaultPlugins) {
      const handled = plugin(e, context);
      if (handled) {
        return;
      }
    }

    defaultErrorHandlingPlugin(e, context);
  };

  return useMutation(
    async (values) => {
      if (onBeforeAction) {
        const shouldProceed = await onBeforeAction({
          formik,
          modalControl,
          requestOrRequestType,
          requestActionName,
          actionExtraContext,
        });
        if (!shouldProceed) {
          modalControl?.closeModal();
          throw new Error("Could not proceed with the action.");
        }
      }
      const formValues = { ...formik?.values };
      if (values) {
        formValues.payload.content = values;
      }
      return action(requestOrRequestType, formValues);
    },
    {
      onError: handleActionError,
      onSuccess: (data, variables) => {
        if (onAfterAction) {
          onAfterAction({
            data,
            variables,
            formik,
            modalControl,
            requestOrRequestType,
            requestActionName,
            actionExtraContext,
          });
        }
        const redirectionURL =
          data?.data?.links?.ui_redirect_url ||
          data?.data?.links?.topic?.self_html;

        modalControl?.closeModal();

        if (redirectionURL) {
          window.location.href = redirectionURL;
        } else {
          window.location.reload();
        }
      },
    }
  );
};
