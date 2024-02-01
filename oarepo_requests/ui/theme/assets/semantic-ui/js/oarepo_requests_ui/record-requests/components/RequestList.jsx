import React from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { List, Segment, SegmentGroup, Header, Button } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import _truncate from "lodash/truncate";

import { RequestModal } from ".";

/**
 * @typedef {import("../types").Request} Request
 * @typedef {import("../types").RequestTypeEnum} RequestTypeEnum
 */

/**
 * @param {{ requests: Request[], requestModalType: RequestTypeEnum }} props
 */
export const RequestList = ({ requests, requestTypes, requestModalType }) => {
  return (
    <List link divided relaxed>
      {requests.map((request) => {
        let modalType = requestModalType;
        if (_isEmpty(requestModalType)) {
          if ("submit" in request.links?.actions) {
            modalType = "submit";
          } else if ("cancel" in request.links?.actions) {
            modalType = "cancel";
          }
        }
        return (
          <RequestModal key={request.uuid} request={request} requestTypes={requestTypes} requestModalType={modalType}
            triggerButton={
              <List.Item as="a" key={request.id}>
                <List.Content floated="right" verticalAlign="middle">
                  <div style={{ textAlign: "right" }}>{request?.status ?? i18next.t("No status")}</div>
                  <div>{new Date(request.created)?.toLocaleString("cs-CZ")}</div>
                </List.Content>
                <List.Content>
                  <List.Header>{request.name}</List.Header>
                  <List.Description>{_truncate(request.description, { length: 30 })}</List.Description>
                </List.Content>
              </List.Item>
            }
          />
        )
      })}
    </List>
  )
};

RequestList.propTypes = {
  requests: PropTypes.array.isRequired,
  requestTypes: PropTypes.array.isRequired,
  requestModalType: PropTypes.oneOf(["create", "accept", "submit", "cancel"])
};