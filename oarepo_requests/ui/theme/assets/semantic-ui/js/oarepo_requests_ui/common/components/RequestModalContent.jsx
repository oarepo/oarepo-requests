import React from "react";
import PropTypes from "prop-types";
import { Grid } from "semantic-ui-react";
import {
  SideRequestInfo,
  RequestCustomFields,
  Timeline,
} from "@js/oarepo_requests_common";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import sanitizeHtml from "sanitize-html";
import { InvenioRequestsApp } from "@js/invenio_requests/InvenioRequestsApp";
import defaultOverrides from "@js/oarepo_requests_common/defaultOverrides";
import { overrideStore } from "react-overridable";
import { RequestDetails } from "../RequestDetail";

/**
 * @typedef {import("../../record-requests/types").Request} Request
 * @typedef {import("../../record-requests/types").RequestTypeEnum} RequestTypeEnum
 * @typedef {import("../../record-requests/types").Event} Event
 */

/** @param {{ request: Request, requestModalType: RequestTypeEnum, }} props */
export const RequestModalContent = ({
  request,
  customFields,
  allowedHtmlAttrs,
  allowedHtmlTags,
}) => {
  /** @type {{requests: Request[], setRequests: (requests: Request[]) => void}} */
  console.log("RequestModalContent render", request);
  const description = request?.stateful_description || request?.description;

  const sanitizedDescription = sanitizeHtml(description, {
    allowedTags: allowedHtmlTags,
    allowedAttributes: allowedHtmlAttrs,
  });
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
      // config={config}
    />
  );
};

RequestModalContent.propTypes = {
  request: PropTypes.object.isRequired,
  customFields: PropTypes.object,
  allowedHtmlAttrs: PropTypes.object,
  allowedHtmlTags: PropTypes.array,
};
