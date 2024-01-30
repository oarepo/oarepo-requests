import React, { useContext } from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { List, Segment, SegmentGroup, Header, Button } from "semantic-ui-react";

import { RequestList } from ".";
import { RequestContext } from "../contexts";

/**
 * @typedef {import("../types").Request} Request
 * @typedef {import("../types").RequestType} RequestType
 */
/**
 * @param {{ requests: Request[], requestTypes: RequestType[] }} props
 */
export const RequestListContainer = ({ requestTypes }) => {
  const TriggerButtonForRequest = ({ onClick, request }) => (
    <List.Item as={Button} onClick={onClick} inverted basic fluid style={{ textAlign: "left" }}>
      {/* <List.Content floated="right" verticalAlign="middle">
                    <RequestModal request={request} triggerButton={<Button compact size="medium" title={`${i18next.t("Open dialog for request")} ${request.id}`} content="Open Dialog" />} />
                  </List.Content> */}
      <List.Content>
        <List.Header>
          {request.name}
        </List.Header>
        <List.Description>
          {request.description}
        </List.Description>
      </List.Content>
    </List.Item>
  );

  const [requests, setRequests] = useContext(RequestContext);

  let requestsToApprove = [];
  let otherRequests = [];
  for (const request of requests) {
    if ("accept" in request.links?.actions) {
      requestsToApprove.push(request);
    } else {
      otherRequests.push(request);
    }
  }

  const SegmentGroupOrEmpty = requestsToApprove.length > 0 && otherRequests.length > 0 ? SegmentGroup : <></>;

  return (
    <SegmentGroupOrEmpty>
      <Segment className="requests-my-requests">
        <Header size="medium">{i18next.t("My Requests")}</Header>
        <RequestList requests={otherRequests} requestTypes={requestTypes} />
      </Segment>
      {requestsToApprove.length > 0 && (
        <Segment className="requests-requests-to-approve">
          <Header size="medium">{i18next.t("Requests to Approve")}</Header>
          <RequestList requests={requestsToApprove} requestTypes={requestTypes} requestModalType="accept" />
        </Segment>
      )}
    </SegmentGroupOrEmpty>
  );
};
