import React from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { List } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import _sortBy from "lodash/sortBy";

/** 
 * @typedef {import("../types").Request} Request
 * @typedef {import("../types").RequestType} RequestType
 */

/** @param {{ request: Request, requestType: RequestType, isSidebar: boolean }} props */
export const ModalContentSideInfo = ({ request, requestType, isSidebar = false }) => {
  return (
    <List divided={isSidebar} relaxed={isSidebar}>
      <List.Item>
        <List.Content>
          <List.Header>{i18next.t("Creator")}</List.Header>
          {request.created_by?.link && <a href={request.created_by.link}>{request.created_by.label}</a> || request.created_by?.label}
        </List.Content>
      </List.Item>
      <List.Item>
        <List.Content>
          <List.Header>{i18next.t("Receiver")}</List.Header>
          {request.receiver?.link && <a href={request.receiver?.link}>{request.receiver?.label}</a> || request.receiver?.label}
        </List.Content>
      </List.Item>
      <List.Item>
        <List.Content>
          <List.Header>{i18next.t("Request type")}</List.Header>
          {requestType.name}
        </List.Content>
      </List.Item>
      <List.Item>
        <List.Content>
          <List.Header>{i18next.t("Created")}</List.Header>
          {`${Math.ceil(Math.abs(new Date(request?.created) - new Date()) / 3.6e6)} hours ago`}
        </List.Content>
      </List.Item>
    </List>
  )
};
