import { setIn } from "formik";
import { serializeErrors } from "@js/oarepo_ui/forms";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { encodeUnicodeBase64 } from "@js/oarepo_ui";

export const cfValidationErrorPlugin = (e, { formik }) => {
  if (
    e?.response?.data?.error_type === "cf_validation_error" &&
    e?.response?.data?.errors
  ) {
    let errorsObj = {};
    for (const error of e.response.data.errors) {
      errorsObj = setIn(errorsObj, error.field, error.messages.join(" "));
    }
    formik?.setErrors(errorsObj);
    return true;
  }
  return null;
};

export const recordValidationErrorsPlugin = (
  e,
  { modalControl, actionExtraContext: { setErrors } }
) => {
  if (e?.response?.data?.errors?.length > 0) {
    const errors = serializeErrors(
      e?.response?.data?.errors,
      i18next.t(
        "Action failed due to validation errors. Please correct the errors and try again:"
      )
    );
    setErrors(errors);
    modalControl?.closeModal();
    return true;
  }
  return null;
};

export const handleRedirectToEditFormPlugin = (
  e,
  { formik, modalControl, actionExtraContext: { record } }
) => {
  if (e?.response?.data?.errors && record?.links?.edit_html) {
    const errorData = e.response.data;
    const jsonErrors = JSON.stringify(errorData);
    const base64EncodedErrors = encodeUnicodeBase64(jsonErrors);

    formik?.setFieldError(
      "api",
      i18next.t("Record has validation errors. Redirecting to form...")
    );

    setTimeout(() => {
      window.location.href = record.links.edit_html + `#${base64EncodedErrors}`;
      modalControl?.closeModal();
    }, 2500);

    return true;
  }
  return null;
};

export const defaultErrorHandlingPlugin = (e, { formik }) => {
  if (e?.response?.data?.errors) {
    formik?.setFieldError(
      "api",
      i18next.t(
        "The request could not be created due to validation errors. Please correct the errors and try again."
      )
    );
  } else {
    formik?.setFieldError(
      "api",
      i18next.t(
        "The action could not be executed. Please try again in a moment."
      )
    );
  }
};
