import axios from "axios";
import _isEmpty from "lodash/isEmpty";
import _isFunction from "lodash/isFunction";

export const serializeCustomFields = (formData) => {
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
