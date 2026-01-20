import React from "react";
import PropTypes from "prop-types";
import { Button } from "semantic-ui-react";
import { RequestModal, RequestModalContent } from ".";
import { useRequestContext } from "@js/oarepo_requests_common";
import { useIsMutating } from "@tanstack/react-query";
import { useCallbackContext, FormikRefContextProvider } from "../../common";

/**
 * @typedef {import("../types").Request} Request
 */

/**
 * @param {{ requests: Request[] }} props
 */
export const RequestList = ({ requests }) => {
  const { actionsLocked } = useCallbackContext();
  const { requestButtonsIconsConfig } = useRequestContext();
  const isMutating = useIsMutating();
  return requests.map((request) => {
    const buttonIconProps =
      requestButtonsIconsConfig[request.status_code] ||
      requestButtonsIconsConfig?.default;
    const header = request?.stateful_name || request?.name || request.type;
    return (
      <FormikRefContextProvider key={request.id}>
        <RequestModal
          key={request.id}
          request={request}
          requestType={request}
          header={header}
          requestCreationModal={false}
          trigger={
            <Button
              className={`requests request-reply-button ${request.type} ${request.type}-${request.status_code}`}
              fluid
              title={header}
              content={header}
              disabled={actionsLocked || isMutating > 0}
              labelPosition="left"
              {...buttonIconProps}
            />
          }
          ContentComponent={RequestModalContent}
        />
      </FormikRefContextProvider>
    );
  });
};

RequestList.propTypes = {
  requests: PropTypes.array.isRequired,
};
