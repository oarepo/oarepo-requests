import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Placeholder, Message } from "semantic-ui-react";
import { RequestList } from ".";
import PropTypes from "prop-types";

/**
 * @param {{ requestsLoading: boolean, requestsLoadingError: Error }} props
 */
export const RequestListContainer = ({
  requestsLoading,
  requestsLoadingError,
  openRequests,
}) => {
  return (
    <div className="requests-my-requests borderless">
      {requestsLoading && (
        <Placeholder fluid>
          {Array.from({ length: 2 }).map((_, index) => (
            // eslint-disable-next-line react/no-array-index-key
            <Placeholder.Paragraph key={index}>
              <Placeholder.Line length="full" />
              <Placeholder.Line length="medium" />
            </Placeholder.Paragraph>
          ))}
        </Placeholder>
      )}

      {requestsLoadingError && (
        <Message negative>
          <Message.Header>{i18next.t("Error loading requests")}</Message.Header>
        </Message>
      )}

      {!requestsLoading && !requestsLoadingError && (
        <RequestList requests={openRequests} />
      )}
    </div>
  );
};

RequestListContainer.propTypes = {
  requestsLoading: PropTypes.bool.isRequired,
  // eslint-disable-next-line react/require-default-props -- Error object or null by default
  requestsLoadingError: PropTypes.object,
  openRequests: PropTypes.array,
};
