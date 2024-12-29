/*
 * Copyright (C) 2024 CESNET z.s.p.o.
 *
 * oarepo-requests is free software; you can redistribute it and/or
 * modify it under the terms of the MIT License; see LICENSE file for more
 * details.
 */
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { useMutation } from "@tanstack/react-query";
import { useCallbackContext } from "@js/oarepo_requests_common";

export const useAction = ({
  action,
  requestOrRequestType,
  formik,
  modalControl,
  requestActionName,
} = {}) => {
  const { onBeforeAction, onAfterAction, onActionError } = useCallbackContext();
  return useMutation(
    async (values) => {
      if (onBeforeAction) {
        const shouldProceed = await onBeforeAction({
          formik,
          modalControl,
          requestOrRequestType,
          requestActionName,
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
      onError: (e, variables) => {
        if (onActionError) {
          onActionError({
            e,
            variables,
            formik,
            modalControl,
            requestOrRequestType,
            requestActionName,
          });
        } else if (e?.response?.data?.errors) {
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
      },
      onSuccess: (data, variables) => {
        if (onAfterAction) {
          onAfterAction({
            data,
            variables,
            formik,
            modalControl,
            requestOrRequestType,
            requestActionName,
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
