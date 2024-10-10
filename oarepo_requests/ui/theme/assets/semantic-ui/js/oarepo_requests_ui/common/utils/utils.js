import _isEmpty from "lodash/isEmpty";
import { http } from "@js/oarepo_ui";
import _set from "lodash/set";

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
