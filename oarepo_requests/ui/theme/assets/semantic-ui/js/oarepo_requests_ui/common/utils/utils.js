import _isEmpty from "lodash/isEmpty";
import { http } from "@js/oarepo_ui";

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
  return await http.post(request.links?.actions?.accept, formData);
};

export const decline = async (request, formData) => {
  return await http.post(request.links?.actions?.decline, formData);
};

export const cancel = async (request, formData) => {
  return await http.post(request.links?.actions?.cancel, formData);
};
