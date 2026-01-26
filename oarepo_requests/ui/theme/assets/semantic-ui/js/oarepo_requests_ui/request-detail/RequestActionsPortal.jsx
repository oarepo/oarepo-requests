import PropTypes from "prop-types";
import ReactDOM from "react-dom";
import React from "react";
import { useFormikRefContext } from "../common";
import { RequestActionController } from "@js/oarepo_requests_common";

const element = document.getElementById("request-actions");

export const RequestActionsPortal = ({ request, actionSuccessCallback }) => {
  const formikRef = useFormikRefContext();
  return ReactDOM.createPortal(
    <RequestActionController
      request={request}
      actionSuccessCallback={actionSuccessCallback}
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
