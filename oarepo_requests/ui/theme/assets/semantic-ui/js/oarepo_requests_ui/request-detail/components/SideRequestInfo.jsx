import React from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Icon, List } from "semantic-ui-react";

import { getRequestStatusIcon } from "../utils";

/** 
 * @typedef {import("../types").Request} Request
 */

/** @param {{ request: Request }} props */
export const SideRequestInfo = ({ request }) => {
  const statusIcon = getRequestStatusIcon(request?.status_code);

  return (
    <List horizontal relaxed divided size="small">
      <List.Item>
        <List.Header as="h3">
          {i18next.t("Creator")}
        </List.Header>
        <List.Content>
          <Icon name="user circle outline" />
          <span>{request.created_by?.link && <a href={request.created_by.link}>{request.created_by.label}</a> || request.created_by?.label}</span>
        </List.Content>
      </List.Item>
      
      <List.Item>
        <List.Header as="h3">
          {i18next.t("Receiver")}
        </List.Header>
        <List.Content>
          <Icon name="mail outline" />
          <span>{request.receiver?.link && <a href={request.receiver?.link}>{request.receiver?.label}</a> || request.receiver?.label}</span>
        </List.Content>
      </List.Item>

      {/* <Header as="h3"  size="tiny">
        {i18next.t("Request type")}
      </Header>
      <Label size="small">{request?.type}</Label>

      <Divider /> */}

      <List.Item>
        <List.Header as="h3">
          {i18next.t("Status")}
        </List.Header>
        <List.Content>
          {statusIcon && <Icon name={statusIcon.name} color={statusIcon.color} />}
          <span>{request?.status}</span>
        </List.Content>
      </List.Item>

      <List.Item>
        <List.Header as="h3">
          {i18next.t("Created")}
        </List.Header>
        <List.Content>
          {request?.created}
        </List.Content>
      </List.Item>
    </List>
  )
};
