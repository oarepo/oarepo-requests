import React from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";

import { Segment, Header, Button, Dimmer, Loader, Placeholder, Message } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";

import { RequestModal } from "./RequestModal";

/**
 * @typedef {import("../types").Request} Request
 * @typedef {import("../types").RequestType} RequestType
 */

/**
 * @param {{ requestTypes: RequestType[], isLoading: boolean, loadingError: Error, fetchNewRequests: () => void }} props
 */
export const CreateRequestButtonGroup = ({ requestTypes, isLoading, loadingError, fetchNewRequests }) => {
  const createRequests = requestTypes.filter(requestType => requestType.links.actions?.create);

  return (
    <Segment>
      <Header size="small" className="detail-sidebar-header">{i18next.t("Create Request")}</Header>
      <Dimmer.Dimmable dimmed={isLoading}>
        <Dimmer active={isLoading} inverted>
          <Loader indeterminate>{i18next.t("Loading request types")}...</Loader>
        </Dimmer>
        {isLoading ? <Placeholder fluid>
          {Array.from({ length: 3 }).map((_, index) => (
            <Placeholder.Paragraph key={index}>
              <Placeholder.Line length="full" />
              <Placeholder.Line length="medium" />
              <Placeholder.Line length="short" />
            </Placeholder.Paragraph>
          ))}
        </Placeholder> :
          loadingError ?
            <Message negative>
              <Message.Header>{i18next.t("Error loading request types")}</Message.Header>
              <p>{loadingError?.message}</p>
            </Message> :
            !_isEmpty(createRequests) ?
              <Button.Group vertical compact fluid>
                {createRequests.map((requestType) => (
                  <RequestModal
                    key={requestType.type_id}
                    request={requestType}
                    requestModalType="create"
                    triggerButton={<Button icon="plus" className="pl-0" title={i18next.t(requestType.name)} basic compact content={requestType.name} />}
                    fetchNewRequests={fetchNewRequests}
                  />
                ))}
              </Button.Group> :
              <p>{i18next.t("No new requests to create")}.</p>
        }
      </Dimmer.Dimmable>
    </Segment>
  );
}