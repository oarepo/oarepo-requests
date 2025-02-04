/*
 * Copyright (C) 2024 CESNET z.s.p.o.
 *
 * oarepo-requests is free software; you can redistribute it and/or
 * modify it under the terms of the MIT License; see LICENSE file for more
 * details.
 */
import React from "react";
import ReactDOM from "react-dom";
import { RecordRequests } from "./components";
import { encodeUnicodeBase64 } from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { setIn } from "formik";

const recordRequestsAppDiv = document.getElementById("record-requests");

if (recordRequestsAppDiv) {
  const record = JSON.parse(recordRequestsAppDiv.dataset.record);

  const onActionError = ({ e, formik, modalControl }) => {
    if (
      e?.response?.data?.error_type === "cf_validation_error" &&
      e?.response?.data?.errors
    ) {
      let errorsObj = {};
      for (const error of e.response.data.errors) {
        errorsObj = setIn(errorsObj, error.field, error.messages.join(" "));
      }
      formik?.setErrors(errorsObj);
    } else if (e?.response?.data?.errors) {
      const errorData = e.response.data;
      const jsonErrors = JSON.stringify(errorData);
      const base64EncodedErrors = encodeUnicodeBase64(jsonErrors);
      if (record?.links?.edit_html) {
        formik?.setFieldError(
          "api",
          i18next.t("Record has validation errors. Redirecting to form...")
        );
        setTimeout(() => {
          window.location.href =
            record.links.edit_html + `#${base64EncodedErrors}`;
          modalControl?.closeModal();
        }, 2500);
      }
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
  };
  ReactDOM.render(
    <RecordRequests record={record} onActionError={onActionError} />,
    recordRequestsAppDiv
  );
}
