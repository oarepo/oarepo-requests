import _isEmpty from "lodash/isEmpty";

export default function isDeepEmpty(input) {
  if(_isEmpty(input)) {
    return true;
  }
  if(typeof input === 'object') {
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
