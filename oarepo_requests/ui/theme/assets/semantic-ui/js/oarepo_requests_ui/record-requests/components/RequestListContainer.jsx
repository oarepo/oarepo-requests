import React from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Segment, Header, Dimmer, Loader, Placeholder, Message } from "semantic-ui-react";
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

  let openRequests = requests.filter(request => request.is_open);

  return (
    <Segment className="requests-my-requests borderless">
      <Header size="tiny" className="detail-sidebar-header">{i18next.t("Pending")}</Header>
      {isLoading ?
        <Placeholder fluid>
          <Placeholder.Paragraph>
            <Placeholder.Line length="full" />
            <Placeholder.Line length="medium" />
          </Placeholder.Paragraph>
        </Placeholder> :
        loadingError ?
          <Message negative>
            <Message.Header>{i18next.t("Error loading requests")}</Message.Header>
            <p>{loadingError?.message}</p>
          </Message> :
          !_isEmpty(openRequests) &&
          <RequestList requests={openRequests} requestTypes={requestTypes} />
      }
    </Segment>
  );
};
