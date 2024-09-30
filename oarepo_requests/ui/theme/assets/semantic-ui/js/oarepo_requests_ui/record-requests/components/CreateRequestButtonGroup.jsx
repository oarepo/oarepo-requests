import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Placeholder, Message } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import { RequestModal, CreateRequestModalContent } from ".";
import { useRequestContext } from "../contexts";
import PropTypes from "prop-types";

/**
 * @param {{  applicableRequestsLoading: boolean, applicableRequestsLoadingError: Error }} props
 */
export const CreateRequestButtonGroup = ({
  applicableRequestsLoading,
  applicableRequestsLoadingError,
}) => {
  const { requestTypes, requestButtonsIconsConfig } = useRequestContext();
  const createRequests = requestTypes?.filter(
    (requestType) => requestType.links.actions?.create
  );

  if (applicableRequestsLoading) {
    return (
      <div className="requests-create-request-buttons borderless">
        <Placeholder>
          {Array.from({ length: 2 }).map((_, index) => (
            <Placeholder.Paragraph key={index}>
              <Placeholder.Line length="full" />
              <Placeholder.Line length="medium" />
            </Placeholder.Paragraph>
          ))}
        </Placeholder>
      </div>
    );
  }

  if (applicableRequestsLoadingError) {
    return (
      <div className="requests-create-request-buttons borderless">
        <Message negative>
          <Message.Header>
            {i18next.t("Error loading request types")}
          </Message.Header>
        </Message>
      </div>
    );
  }

  if (_isEmpty(createRequests)) {
    return null;
  }

  return (
    <div className="requests-create-request-buttons borderless">
      {createRequests.map((requestType) => {
        const header =
          requestType?.stateful_name ||
          requestType?.name ||
          requestType?.type_id;
        const buttonIconProps = requestButtonsIconsConfig[requestType.type_id];
        return (
          <RequestModal
            key={requestType.type_id}
            requestType={requestType}
            header={header}
            requestCreationModal
            trigger={
              <Button
                // applicable requests don't have a status
                className={`requests request-create-button ${requestType?.type_id}`}
                fluid
                title={i18next.t(requestType.name)}
                content={i18next.t(requestType.name)}
                {...buttonIconProps}
              />
            }
            ContentComponent={CreateRequestModalContent}
          />
        );
      })}
    </div>
  );
};

CreateRequestButtonGroup.propTypes = {
  applicableRequestsLoading: PropTypes.bool,
  applicableRequestsLoadingError: PropTypes.object,
};
