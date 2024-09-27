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

export const fetchUpdated = async (url, setter, onError) => {
  return axios({
    method: "get",
    url: url,
    headers: {
      "Content-Type": "application/json",
      Accept: "application/vnd.inveniordm.v1+json",
    },
  })
    .then((response) => {
      setter(response.data);
    })
    .catch((error) => {
      if (!_isFunction(onError)) {
        throw error;
      }
      onError(error);
    });
};
