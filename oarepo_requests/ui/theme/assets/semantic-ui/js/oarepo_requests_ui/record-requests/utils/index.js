import _sortBy from "lodash/sortBy";
import _concat from "lodash/concat";
import _has from "lodash/has";
import _partition from "lodash/partition";
import _isEmpty from "lodash/isEmpty";

export function sortByStatusCode(requests) {
  if (!_has(requests[0], "status_code")) {
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
    for(const item of Object.values(input)) {
      // if item is not undefined and is a primitive, return false
      // otherwise dig deeper
      if((item !== undefined && typeof item !== 'object') || !isDeepEmpty(item)) {
        return false
      }
    }
    return true;
  }
  return _isEmpty(input);
}
