import { REQUEST_TYPE } from "../../utils/objects";
import Accept from "./Accept";
import Decline from "./Decline";
import Cancel from "./Cancel";
import Create from "./Create";
import Submit from "./Submit";
import Save from "./Save";
import CreateAndSubmit from "./CreateAndSubmit";
import CreateSubmitAction from "./CreateSubmitAction";

export const mapLinksToActions = (requestOrRequestType, customFields) => {
  const actionComponents = [];
  for (const actionKey of Object.keys(requestOrRequestType.links?.actions)) {
    switch (actionKey) {
      case REQUEST_TYPE.ACCEPT:
        actionComponents.push({ name: REQUEST_TYPE.ACCEPT, component: Accept });
        actionComponents.push({
          name: REQUEST_TYPE.DECLINE,
          component: Decline,
        });
        break;
      case REQUEST_TYPE.CANCEL:
        actionComponents.push({ name: REQUEST_TYPE.CANCEL, component: Cancel });
        break;
      case REQUEST_TYPE.CREATE:
        // requestOrRequestType is requestType here
        if (customFields?.ui) {
          actionComponents.push({
            name: REQUEST_TYPE.CREATE,
            component: Create,
          });
        }
        actionComponents.push({
          name: REQUEST_TYPE.SUBMIT,
          component: CreateAndSubmit,
        });
        break;
      case REQUEST_TYPE.SUBMIT:
        actionComponents.push({ name: REQUEST_TYPE.SUBMIT, component: Submit });
        if (customFields?.ui) {
          actionComponents.push({ name: REQUEST_TYPE.SAVE, component: Save });
        }
        break;
      default:
        break;
    }
  }
  return actionComponents;
};

export {
  Accept,
  Decline,
  Cancel,
  Create,
  Submit,
  Save,
  CreateAndSubmit,
  CreateSubmitAction,
};
