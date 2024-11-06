import _isEmpty from "lodash/isEmpty";
import { http } from "@js/oarepo_ui";
import _set from "lodash/set";
import _has from "lodash/has";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import * as Yup from "yup";

export const hasAll = (obj, ...keys) => keys.every((key) => _has(obj, key));

export const hasAny = (obj, ...keys) => keys.some((key) => _has(obj, key));

export const CommentPayloadSchema = Yup.object().shape({
  payload: Yup.object().shape({
    content: Yup.string()
      .min(1, i18next.t("Comment must be at least 1 character long."))
      .required(i18next.t("Comment must be at least 1 character long.")),
    format: Yup.string().equals(["html"], i18next.t("Invalid format.")),
  }),
});

export const getRequestStatusIcon = (requestStatus) => {
  switch (requestStatus?.toLowerCase()) {
    case "created":
      return { name: "clock outline", color: "grey" };
    case "submitted":
      return { name: "clock", color: "grey" };
    case "cancelled":
      return { name: "close", color: "red" };
    case "accepted":
      return { name: "check circle", color: "green" };
    case "declined":
      return { name: "close", color: "red" };
    case "expired":
      return { name: "hourglass end", color: "orange" };
    case "deleted":
      return { name: "thrash", color: "black" };
    default:
      return null;
  }
};

export const getFeedMessage = (requestStatus) => {
  switch (requestStatus?.toLowerCase()) {
    case "created":
      return i18next.t("requestCreated");
    case "submitted":
      return i18next.t("requestSubmitted");
    case "cancelled":
      return i18next.t("requestCancelled");
    case "accepted":
      return i18next.t("requestAccepted");
    case "declined":
      return i18next.t("requestDeclined");
    case "expired":
      return i18next.t("Request expired.");
    case "deleted":
      return i18next.t("requestDeleted");
    default:
      return i18next.t("requestCommented");
  }
};

export const serializeCustomFields = (formData) => {
  if (!formData) return {};
  if (
    _isEmpty(formData.payload) ||
    Object.values(formData.payload).every((value) => !value)
  ) {
    return {};
  } else {
    for (let customField of Object.keys(formData.payload)) {
      if (!formData.payload[customField]) {
        delete formData.payload[customField];
      }
    }
    if (_isEmpty(formData.payload)) {
      return {};
    } else {
      return { payload: formData.payload };
    }
  }
};

export const saveAndSubmit = async (request, formValues) => {
  const response = await createOrSave(request, formValues);
  const submittedRequest = await http.post(
    response?.data?.links?.actions?.submit,
    {}
  );
  return submittedRequest;
};

export const createOrSave = async (requestOrRequestType, formValues) => {
  const customFieldsData = serializeCustomFields(formValues);
  if (requestOrRequestType?.links?.actions?.create) {
    return await http.post(
      requestOrRequestType.links.actions.create,
      customFieldsData
    );
  } else {
    return await http.put(requestOrRequestType?.links?.self, customFieldsData);
  }
};

export const accept = async (request, formData) => {
  return await http.post(
    request.links?.actions?.accept,
    serializeDataForInvenioApi(formData)
  );
};

export const decline = async (request, formData) => {
  return await http.post(
    request.links?.actions?.decline,
    serializeDataForInvenioApi(formData)
  );
};

export const cancel = async (request, formData) => {
  return await http.post(
    request.links?.actions?.cancel,
    serializeDataForInvenioApi(formData)
  );
};

// this is not nice, but unfortunately, as our API vs invenio API are not consistent, I don't see a better way (Invenio api accepts only payload.content and nothing else)
const serializeDataForInvenioApi = (formData) => {
  const serializedData = {};
  if (formData.payload?.content) {
    _set(serializedData, "payload.content", formData.payload.content);
  }
  return serializedData;
};
