import React, { useCallback } from "react";
import PropTypes from "prop-types";

import { Button } from "semantic-ui-react";
import { useIsMutating } from "@tanstack/react-query";

import { RequestModal, RequestModalContent, RequestsPerCategory } from ".";
import { useRequestContext } from "@js/oarepo_requests_common";
import { useCallbackContext } from "../../common";

/**
 * @typedef {import("../types").Request} Request
 */

/**
 * @param {{ requests: Request[] }} props
 */
export const RequestList = ({ requests }) => {
  const { actionsLocked, setActionsLocked } = useCallbackContext();
  const { requestButtonsIconsConfig } = useRequestContext();
  const isMutating = useIsMutating();

  const mapRequestToModalComponent = useCallback((request) => {
    const buttonIconProps =
      requestButtonsIconsConfig[request.status_code] ||
      requestButtonsIconsConfig?.default;
    const header = request?.stateful_name || request?.name;
    const description = request?.stateful_description || request?.description;

    return (
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
            title={description}
            content={header}
            onClick={() => setActionsLocked(true)}
            disabled={actionsLocked || isMutating > 0}
            labelPosition="right center"
            {...buttonIconProps}
          />
        }
        ContentComponent={RequestModalContent}
      />
    );
  }, [requestButtonsIconsConfig, actionsLocked, isMutating, setActionsLocked]);

  return (
    <RequestsPerCategory
      requests={requests}
      mapRequestToModalComponent={mapRequestToModalComponent}
    />
  );
};

RequestList.propTypes = {
  requests: PropTypes.array.isRequired,
};
