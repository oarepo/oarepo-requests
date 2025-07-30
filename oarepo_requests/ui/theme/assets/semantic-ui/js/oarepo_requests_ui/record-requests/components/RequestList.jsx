import React from "react";
import PropTypes from "prop-types";

import { Button } from "semantic-ui-react";
import { useIsMutating } from "@tanstack/react-query";

import { RequestModal, RequestModalContent, RequestButtons } from ".";
import { useRequestContext } from "@js/oarepo_requests_common";
import { useCallbackContext } from "../../common";

/**
 * @typedef {import("../types").Request} Request
 */

/**
 * Component for rendering individual request buttons
 */
const RequestButtonWrapper = ({ request }) => {
  const { actionsLocked, setActionsLocked } = useCallbackContext();
  const { requestButtonsIconsConfig } = useRequestContext();
  const isMutating = useIsMutating();

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
};

RequestButtonWrapper.propTypes = {
  request: PropTypes.object.isRequired,
};

const mapRequestToModalComponent = (request) => (
  <RequestButtonWrapper key={request.id} request={request} />
);

/**
 * @param {{ requests: Request[] }} props
 */
export const RequestList = ({ requests }) => {
  return (
    <RequestButtons
      requests={requests}
      mapRequestToModalComponent={mapRequestToModalComponent}
    />
  );
};

RequestList.propTypes = {
  requests: PropTypes.array.isRequired,
};
