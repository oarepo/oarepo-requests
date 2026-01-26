import React from "react";
import PropTypes from "prop-types";
import { InvenioRequestsApp } from "@js/invenio_requests/InvenioRequestsApp";
import { overrideStore } from "react-overridable";
import defaultOverrides from "../defaultOverrides";
import { RequestDetails } from "../RequestDetail";
import { useRequestConfigContext } from "../contexts";

/**
 * @typedef {import("../../record-requests/types").Request} Request
 */

/** @param {{ request: Request }} props */
export const RequestModalContent = ({ request }) => {
  const { requestTypeConfig } = useRequestConfigContext();

  const defaultComponents = {
    "InvenioRequests.RequestActionsPortal": () => null,
    "InvenioRequests.RequestDetails.layout": RequestDetails,
    ...defaultOverrides,
    ...overrideStore.getAll(),
  };

  return (
    <InvenioRequestsApp
      request={request}
      defaultQueryParams={10}
      defaultReplyQueryParams={5}
      overriddenCmps={defaultComponents}
      // userAvatar={userAvatar}
      permissions={{}}
      config={requestTypeConfig?.requests_ui_config}
    />
  );
};

RequestModalContent.propTypes = {
  request: PropTypes.object.isRequired,
};
