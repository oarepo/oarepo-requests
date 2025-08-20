import React from "react";
import PropTypes from "prop-types";

import { Placeholder, Message } from "semantic-ui-react";
import { useIsMutating } from "@tanstack/react-query";

import { useRequestContext } from "@js/oarepo_requests_common";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { CreateRequestButton, RequestButtons } from ".";

/**
 * Component for rendering individual create request buttons
 */
const CreateRequestButtonWrapper = ({ requestType }) => {
  const { requestButtonsIconsConfig } = useRequestContext();
  const isMutating = useIsMutating();
  
  const header =
    requestType.stateful_name || requestType.name || requestType.type_id;
  const buttonIconProps =
    requestButtonsIconsConfig[requestType.type_id] ||
    requestButtonsIconsConfig?.default;

  return (
    <CreateRequestButton
      key={requestType.type_id}
      requestType={requestType}
      isMutating={isMutating}
      buttonIconProps={buttonIconProps}
      header={header}
    />
  );
};

CreateRequestButtonWrapper.propTypes = {
  requestType: PropTypes.object.isRequired,
};

const mapRequestTypeToModal = (requestType) => (
  <CreateRequestButtonWrapper key={requestType.type_id} requestType={requestType} />
);

/**
 * @param {{  applicableRequestsLoading: boolean, applicableRequestsLoadingError: Error }} props
 */
export const CreateRequestButtonGroup = ({
  applicableRequestsLoading,
  applicableRequestsLoadingError,
  createRequests,
}) => {
  let content;

  if (applicableRequestsLoading) {
    content = (
      <Placeholder>
        {Array.from({ length: 2 }).map((_, index) => (
          // eslint-disable-next-line react/no-array-index-key
          <Placeholder.Paragraph key={index}>
            <Placeholder.Line length="full" />
            <Placeholder.Line length="medium" />
          </Placeholder.Paragraph>
        ))}
      </Placeholder>
    );
  } else if (applicableRequestsLoadingError) {
    content = (
      <Message negative className="rel-mb-1">
        <Message.Header>
          {i18next.t("Error loading request types")}
        </Message.Header>
      </Message>
    );
  } else {
    content = <RequestButtons requests={createRequests} mapRequestToModalComponent={mapRequestTypeToModal} />;
  }

  return (
    <div className="requests-create-request-buttons borderless">{content}</div>
  );
};

CreateRequestButtonGroup.propTypes = {
  applicableRequestsLoading: PropTypes.bool.isRequired,
  // eslint-disable-next-line react/require-default-props -- Error object or null by default
  applicableRequestsLoadingError: PropTypes.object,
  createRequests: PropTypes.array,
};
