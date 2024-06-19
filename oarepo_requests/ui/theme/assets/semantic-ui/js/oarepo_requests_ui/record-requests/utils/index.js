import axios from "axios";

import _sortBy from "lodash/sortBy";
import _concat from "lodash/concat";
import _has from "lodash/has";
import _partition from "lodash/partition";
import _isEmpty from "lodash/isEmpty";
import _isFunction from "lodash/isFunction";

export function sortByStatusCode(requests) {
  if (_isEmpty(requests)) {
    return requests;
  }
  const [acceptedDeclined, other] = _partition(requests, (r) => r?.status_code == "accepted" || r?.status_code == "declined");
  return _concat(_sortBy(other, "status_code"), _sortBy(acceptedDeclined, "status_code"));
}

export function isDeepEmpty(input) {
  if (_isEmpty(input)) {
    return true;
  }
  if (typeof input === 'object') {
    for (const item of Object.values(input)) {
      // if item is not undefined and is a primitive, return false
      // otherwise dig deeper
      if ((item !== undefined && typeof item !== 'object') || !isDeepEmpty(item)) {
        return false
      }
    }
    return true;
  }
  return _isEmpty(input);
}

export const fetchUpdated = async (url, setter, onError) => {
  return axios({
    method: 'get',
    url: url,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/vnd.inveniordm.v1+json'
    }
  })
    .then(response => {
      setter(response.data);
    })
    .catch(error => {
      if (!_isFunction(onError)) {
        throw error;
      }
      onError(error);
    });
}

export const mapPayloadUiToInitialValues = (payloadUi) => {
  const initialValues = { payload: {} };
  payloadUi?.forEach(section => {
    section.fields.forEach(field => {
      initialValues.payload[field.field] = "";
    });
  });
  return initialValues;
};
