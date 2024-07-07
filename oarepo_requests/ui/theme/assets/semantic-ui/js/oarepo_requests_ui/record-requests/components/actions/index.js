import { REQUEST_TYPE } from "../../utils/objects";
import Accept from "./Accept";
import Decline from "./Decline";
import Cancel from "./Cancel";

export const mapLinksToActions = (actionLinks) => {
  const actionComponents = [];
  for (const actionKey of Object.keys(actionLinks)) {
    switch (actionKey) {
      case REQUEST_TYPE.ACCEPT:
        actionComponents.push({ name: REQUEST_TYPE.ACCEPT, component: Accept });
        break;
      case REQUEST_TYPE.DECLINE:
        actionComponents.push({ name: REQUEST_TYPE.DECLINE, component: Decline });
        break;
      case REQUEST_TYPE.CANCEL:
        actionComponents.push({ name: REQUEST_TYPE.CANCEL, component: Cancel });
        break;
      default:
        break;
    }
  }
  return actionComponents;
}

export { Accept, Decline, Cancel };