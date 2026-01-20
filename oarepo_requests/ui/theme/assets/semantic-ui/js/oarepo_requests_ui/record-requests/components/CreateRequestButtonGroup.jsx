import React, { useState, useRef } from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Placeholder, Message } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import {
  useRequestContext,
  useCallbackContext,
} from "@js/oarepo_requests_common";
import PropTypes from "prop-types";
import { CreateRequestButton } from "./CreateRequestButton";
import { RequestActionController } from "../../common";

/**
 * @param {{  applicableRequestsLoading: boolean, applicableRequestsLoadingError: Error }} props
 */
export const CreateRequestButtonGroup = ({
  applicableRequestsLoading,
  applicableRequestsLoadingError,
}) => {
  const { requestTypes, requestButtonsIconsConfig } = useRequestContext();
  const { onAfterAction, fetchNewRequests } = useCallbackContext();
  const createRequests = requestTypes?.filter(
    (requestType) => requestType.links.actions?.create
  );
  let content;
  const actionSuccessCallback = (response) => {
    const redirectionURL =
      response?.data?.links?.ui_redirect_url ||
      response?.data?.links?.topic?.self_html;
    fetchNewRequests();

    if (redirectionURL) {
      window.location.href = redirectionURL;
    }
  };
  if (applicableRequestsLoading) {
    content = (
      <Placeholder>
        {Array.from({ length: 2 }).map((_, index) => (
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
  } else if (_isEmpty(createRequests)) {
    return null; // No need to render anything if there are no requests
  } else {
    content = createRequests.map((requestType) => {
      const header =
        requestType.stateful_name || requestType.name || requestType.type_id;
      const buttonIconProps =
        requestButtonsIconsConfig[requestType.type_id] ||
        requestButtonsIconsConfig?.default;

      return (
        <RequestActionController
          key={requestType.type_id}
          renderAllActions={false}
          request={requestType}
          actionSuccessCallback={onAfterAction ?? actionSuccessCallback}
        >
          <CreateRequestButton
            key={requestType.type_id}
            requestType={requestType}
            buttonIconProps={buttonIconProps}
            header={header}
          />
        </RequestActionController>
      );
    });
  }

  return (
    <div className="requests-create-request-buttons borderless">{content}</div>
  );
};

CreateRequestButtonGroup.propTypes = {
  applicableRequestsLoading: PropTypes.bool,
  applicableRequestsLoadingError: PropTypes.object,
};
