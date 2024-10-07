import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Placeholder, Message, Confirm } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import { RequestModal, CreateRequestModalContent } from ".";
import {
  useRequestContext,
  CreateSubmitAction,
  useConfirmModalContext,
} from "@js/oarepo_requests_common";
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
  const { confirmDialogProps } = useConfirmModalContext();

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
        const { dangerous, hasForm } = requestType;
        const needsDialog = dangerous || hasForm;
        const header =
          requestType?.stateful_name ||
          requestType?.name ||
          requestType?.type_id;
        const buttonIconProps = requestButtonsIconsConfig[requestType.type_id];

        if (!hasForm && dangerous) {
          return (
            <CreateSubmitAction
              key={requestType?.type_id}
              requestType={requestType}
              requireConfirmation={dangerous}
            />
          );
        }

        if (!hasForm && !dangerous) {
          return (
            <CreateSubmitAction
              key={requestType?.type_id}
              requestType={requestType}
              requireConfirmation={false}
            />
          );
        }

        if (needsDialog) {
          return (
            <RequestModal
              key={requestType.type_id}
              requestType={requestType}
              header={header}
              requestCreationModal
              trigger={
                <Button
                  className={`requests request-create-button ${requestType?.type_id}`}
                  fluid
                  title={header}
                  content={header}
                  {...buttonIconProps}
                />
              }
              ContentComponent={CreateRequestModalContent}
            />
          );
        }

        return null;
      })}
      <Confirm {...confirmDialogProps} />
    </div>
  );
};

CreateRequestButtonGroup.propTypes = {
  applicableRequestsLoading: PropTypes.bool,
  applicableRequestsLoadingError: PropTypes.object,
};
