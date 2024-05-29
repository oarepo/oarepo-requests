import React from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { List } from "semantic-ui-react";

/** 
 * @typedef {import("../types").Request} Request
 */

/** @param {{ request: Request }} props */
export const SideRequestInfo = ({ request }) => {
  return (
    <List relaxed>
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
          {request?.type}
        </List.Content>
      </List.Item>
      <List.Item>
        <List.Content>
          <List.Header>{i18next.t("Status")}</List.Header>
          {request?.status}
        </List.Content>
      </List.Item>
      <List.Item>
        <List.Content>
          <List.Header>{i18next.t("Created")}</List.Header>
          {request?.created}
        </List.Content>
      </List.Item>
    </List>
  )
};
