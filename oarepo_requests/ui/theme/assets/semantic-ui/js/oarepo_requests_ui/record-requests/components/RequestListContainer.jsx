import React, { useContext } from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Segment, SegmentGroup, Header } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";

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
  const [requests,] = useContext(RequestContext);

  let requestsToApprove = [];
  let otherRequests = [];
  for (const request of requests) {
    if ("accept" in request.links?.actions) {
      requestsToApprove.push(request);
    } else {
      otherRequests.push(request);
    }
  }

  const SegmentGroupOrEmpty = requestsToApprove.length > 0 && otherRequests.length > 0 ? SegmentGroup : React.Fragment;

  return (
    <SegmentGroupOrEmpty>
      <Segment className="requests-my-requests">
        <Header size="small" className="detail-sidebar-header">{i18next.t("My Requests")}</Header>
        {!_isEmpty(otherRequests) ? <RequestList requests={otherRequests} requestTypes={requestTypes} /> : <p>{i18next.t("No requests to show")}.</p>}
      </Segment>
      {requestsToApprove.length > 0 && (
        <Segment className="requests-requests-to-approve">
          <Header size="small" className="detail-sidebar-header">{i18next.t("Requests to Approve")}</Header>
          <RequestList requests={requestsToApprove} requestTypes={requestTypes} requestModalType="accept" />
        </Segment>
      )}
    </SegmentGroupOrEmpty>
  );
};
