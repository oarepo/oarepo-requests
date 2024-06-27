import React from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Segment, SegmentGroup, Header, Dimmer, Loader, Placeholder, Message } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";

import { RequestList } from ".";
import { useRequestContext } from "../contexts";

/**
 * @typedef {import("../types").Request} Request
 * @typedef {import("../types").RequestType} RequestType
 */
/**
 * @param {{ requestTypes: RequestType[], isLoading: boolean, loadingError: Error }} props
 */
export const RequestListContainer = ({ requestTypes, isLoading, loadingError }) => {
  const { requests } = useRequestContext();

  let requestsToApprove = [];
  let otherRequests = [];
  for (const request of requests) {
    if ("accept" in request.links.actions) {
      requestsToApprove.push(request);
    } else {
      otherRequests.push(request);
    }
  }

  const SegmentGroupOrEmpty = requestsToApprove.length > 0 && otherRequests.length > 0 ? SegmentGroup : React.Fragment;

  return (
    (isLoading || loadingError) ?
      <Segment className="requests-my-requests">
        <Header size="small" className="detail-sidebar-header">{i18next.t("Requests")}</Header>
        {loadingError ?
          <Message negative>
            <Message.Header>{i18next.t("Error loading requests")}</Message.Header>
            <p>{loadingError?.message}</p>
          </Message> :
          <Dimmer.Dimmable dimmed={isLoading}>
            <Dimmer active={isLoading} inverted>
              <Loader indeterminate>{i18next.t("Loading requests")}...</Loader>
            </Dimmer>
            <Placeholder fluid>
              {Array.from({ length: 3 }).map((_, index) => (
                <Placeholder.Paragraph key={index}>
                  <Placeholder.Line length="full" />
                  <Placeholder.Line length="medium" />
                  <Placeholder.Line length="short" />
                </Placeholder.Paragraph>
              ))}
            </Placeholder>
          </Dimmer.Dimmable>
        }
      </Segment> :
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
