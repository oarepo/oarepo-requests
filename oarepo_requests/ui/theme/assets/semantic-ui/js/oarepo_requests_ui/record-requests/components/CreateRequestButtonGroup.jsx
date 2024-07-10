import React from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Segment, Header, Button, Placeholder, Message, Icon } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";

import { RequestModal, CreateRequestModalContent } from ".";
import { mapLinksToActions } from "./actions";
import { useRequestContext } from "../contexts";

/**
 * @typedef {import("../types").Request} Request
 * @typedef {import("../types").RequestType} RequestType
 */

/**
 * @param {{ requestTypes: RequestType[], isLoading: boolean, loadingError: Error }} props
 */
export const CreateRequestButtonGroup = ({ recordLoading, recordLoadingError }) => {
  const { requestTypes } = useRequestContext();
  const createRequests = requestTypes.filter(requestType => requestType.links.actions?.create);

  return (
    <Segment className="requests-create-request-buttons borderless">
      <Header size="small" className="detail-sidebar-header">{i18next.t("Requests")}</Header>
      {recordLoading ?
        <Placeholder>
          {Array.from({ length: 2 }).map((_, index) => (
            <Placeholder.Paragraph key={index}>
              <Icon name="plus" disabled />
            </Placeholder.Paragraph>
          ))}
        </Placeholder> :
        recordLoadingError ?
          <Message negative>
            <Message.Header>{i18next.t("Error loading request types")}</Message.Header>
            <p>{recordLoadingError?.message}</p>
          </Message> :
          !_isEmpty(createRequests) ?
            <Button.Group vertical compact fluid>
              {createRequests.map((requestType) => {
                const modalActions = mapLinksToActions(requestType);
                return (
                  <RequestModal
                    key={requestType.type_id}
                    requestType={requestType}
                    trigger={
                      <Button icon="plus" className="pl-0" title={i18next.t(requestType.name)} basic compact content={requestType.name} />
                    }
                    actions={modalActions}
                    ContentComponent={CreateRequestModalContent}
                  />
                )
              }
              )}
            </Button.Group> :
            <p>{i18next.t("No new requests to create")}.</p>
      }
    </Segment>
  );
}