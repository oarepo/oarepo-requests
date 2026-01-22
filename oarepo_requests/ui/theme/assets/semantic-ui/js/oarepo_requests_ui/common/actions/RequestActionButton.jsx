import React from "react";
import { Button, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";
import { ConfirmationModal } from "@js/oarepo_requests_common";
import { useConfirmationModal } from "@js/oarepo_ui";
import { useRequestActionContext } from "../contexts";

export const RequestActionButton = ({
  requestOrRequestType,
  extraData,
  iconName,
  buttonLabel,
  requireConfirmation,
  requestActionName,
  ...uiProps
}) => {
  const { isOpen, close, open } = useConfirmationModal();
  const { performAction, cleanError, error, loading } =
    useRequestActionContext();

  const handleClick = () => {
    if (requireConfirmation) {
      open();
    } else {
      performAction(requestActionName);
    }
  };

  return (
    <>
      <Button
        title={buttonLabel}
        onClick={handleClick}
        className="requests request-action-button"
        icon
        labelPosition="left"
        loading={loading}
        disabled={loading}
        {...uiProps}
      >
        <Icon name={iconName} />
        {buttonLabel}
      </Button>
      {isOpen && (
        <ConfirmationModal
          requestActionName={requestActionName}
          requestOrRequestType={requestOrRequestType}
          requestExtraData={extraData}
          onConfirmAction={performAction}
          isOpen={isOpen}
          close={close}
        />
      )}
    </>
  );
};

RequestActionButton.propTypes = {
  requestOrRequestType: PropTypes.object,
  extraData: PropTypes.object,
  iconName: PropTypes.string,
  actionName: PropTypes.string,
  buttonLabel: PropTypes.string,
  requireConfirmation: PropTypes.bool,
  requestActionName: PropTypes.string,
};

export default RequestActionButton;
