import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Placeholder, Message, Icon } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import { RequestModal, CreateRequestModalContent } from ".";
import { useRequestContext } from "../contexts";

/**
 * @param {{  recordLoading: boolean, recordLoadingError: Error }} props
 */
export const CreateRequestButtonGroup = ({
  recordLoading,
  recordLoadingError,
}) => {
  const { requestTypes } = useRequestContext();
  const createRequests = requestTypes.filter(
    (requestType) => requestType.links.actions?.create
  );
  return (
    <div className="requests-create-request-buttons borderless">
      {recordLoading ? (
        <Placeholder>
          {Array.from({ length: createRequests.length }).map((_, index) => (
            <Placeholder.Paragraph key={index}>
              <Icon name="plus" disabled />
            </Placeholder.Paragraph>
          ))}
        </Placeholder>
      ) : recordLoadingError ? (
        <Message negative>
          <Message.Header>
            {i18next.t("Error loading request types")}
          </Message.Header>
        </Message>
      ) : !_isEmpty(createRequests) ? (
        createRequests.map((requestType) => {
          const header = requestType?.name || requestType?.type_id;
          return (
            <RequestModal
              key={requestType.type_id}
              requestType={requestType}
              header={header}
              requestCreationModal
              trigger={
                <Button
                  className={`block request-create-button ${requestType?.type_id} mb-10`}
                  fluid
                  title={i18next.t(requestType.name)}
                  content={requestType.name}
                />
              }
              ContentComponent={CreateRequestModalContent}
            />
          );
        })
      ) : null}
    </div>
  );
};
