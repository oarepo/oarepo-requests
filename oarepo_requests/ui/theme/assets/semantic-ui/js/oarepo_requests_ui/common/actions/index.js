import { REQUEST_TYPE } from "@js/oarepo_requests_common";
import Accept from "./Accept";
import Decline from "./Decline";
import Cancel from "./Cancel";
import Create from "./Create";
import Submit from "./Submit";
import Save from "./Save";
import CreateAndSubmit from "./CreateAndSubmit";
import CreateSubmitAction from "./CreateSubmitAction";

export const mapLinksToActions = (
  requestOrRequestType,
  customFields,
  extra_data
) => {
  const customFieldsPaths = customFields?.ui
    ?.map(({ fields }) => {
      let paths = [];
      for (const field of fields) {
        paths.push(field.field);
      }
      return paths;
    })
    .flat();
  const longForm = customFieldsPaths?.length > 3;
  const actionComponents = [];
  for (const actionKey of Object.keys(requestOrRequestType.links?.actions)) {
    switch (actionKey) {
      case REQUEST_TYPE.ACCEPT:
        actionComponents.push({
          name: REQUEST_TYPE.ACCEPT,
          component: Accept,
          extraData: extra_data,
        });
        actionComponents.push({
          name: REQUEST_TYPE.DECLINE,
          component: Decline,
        });
        break;
      case REQUEST_TYPE.CANCEL:
        actionComponents.push({
          name: REQUEST_TYPE.CANCEL,
          component: Cancel,
          extraData: extra_data,
        });
        break;
      case REQUEST_TYPE.CREATE:
        // requestOrRequestType is requestType here
        if (customFields?.ui && longForm) {
          actionComponents.push({
            name: REQUEST_TYPE.SAVE,
            component: Save,
            extraData: extra_data,
          });
        }
        actionComponents.push({
          name: REQUEST_TYPE.SUBMIT,
          component: CreateAndSubmit,
        });
        break;
      case REQUEST_TYPE.SUBMIT:
        actionComponents.push({
          name: REQUEST_TYPE.SUBMIT,
          component: Submit,
          extraData: extra_data,
        });
        if (customFields?.ui) {
          actionComponents.push({
            name: REQUEST_TYPE.SAVE,
            component: Save,
            extraData: extra_data,
          });
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
