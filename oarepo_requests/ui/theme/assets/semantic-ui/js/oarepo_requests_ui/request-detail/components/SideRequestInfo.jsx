import React from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Header, Divider, Icon, Label } from "semantic-ui-react";

/** 
 * @typedef {import("../types").Request} Request
 */

/** @param {{ request: Request }} props */
export const SideRequestInfo = ({ request }) => {
  return (
    <>
      <Header as="h3" size="tiny">
        {i18next.t("Creator")}
      </Header>
      <div>
        <Icon name="user circle outline" />
        <span>{request.created_by?.link && <a href={request.created_by.link}>{request.created_by.label}</a> || request.created_by?.label}</span>
      </div>

      <Divider />

      <Header as="h3"  size="tiny">
        {i18next.t("Receiver")}
      </Header>
      <div>
        <Icon name="mail outline" />
        <span>{request.receiver?.link && <a href={request.receiver?.link}>{request.receiver?.label}</a> || request.receiver?.label}</span>
      </div>

      <Divider />

      <Header as="h3"  size="tiny">
        {i18next.t("Request type")}
      </Header>
      <Label size="small">{request?.type}</Label>

      <Divider />

      <Header as="h3"  size="tiny">
        {i18next.t("Status")}
      </Header>
      <div>
        <Icon name="clock outline" />
        <span>{request?.status}</span>
      </div>

      <Divider />

      <Header as="h3"  size="tiny">
        {i18next.t("Created")}
      </Header>
      {request?.created}

      <Divider hidden />
    </>
  )
};
