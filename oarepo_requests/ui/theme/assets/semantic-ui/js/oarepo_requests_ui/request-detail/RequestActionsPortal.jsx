import PropTypes from "prop-types";
import ReactDOM from "react-dom";
import React from "react";
import Overridable from "react-overridable";
import { useFormikRefContext } from "../common";
import { OarepoRequestsAPI } from "../common";
import {
  RequestLinksExtractor,
  InvenioRequestsAPI,
} from "@js/invenio_requests/api";
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
    element
  );
};

RequestActionsPortal.propTypes = {
  request: PropTypes.object.isRequired,
  actionSuccessCallback: PropTypes.func.isRequired,
};
