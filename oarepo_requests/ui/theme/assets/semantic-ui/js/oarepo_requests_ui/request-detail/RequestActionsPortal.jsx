import PropTypes from "prop-types";
import ReactDOM from "react-dom";
import React from "react";
import { useFormikRefContext } from "../common";
import { RequestActionController } from "../common/RequestActionController";
import { useCallbackContext } from "../common/contexts/CallbackContext";

const element = document.getElementById("request-actions");

export const RequestActionsPortal = ({ request, actionSuccessCallback }) => {
  const { onErrorPlugins, onBeforeAction, onAfterAction } =
    useCallbackContext() || {};
  const formikRef = useFormikRefContext();
  return ReactDOM.createPortal(
    <RequestActionController
      request={request}
      actionSuccessCallback={onAfterAction ?? actionSuccessCallback}
      onBeforeAction={onBeforeAction}
      onErrorPlugins={onErrorPlugins}
      size="medium"
      formikRef={formikRef}
    />,
    element,
  );
};

RequestActionsPortal.propTypes = {
  request: PropTypes.object.isRequired,
  actionSuccessCallback: PropTypes.func.isRequired,
};
