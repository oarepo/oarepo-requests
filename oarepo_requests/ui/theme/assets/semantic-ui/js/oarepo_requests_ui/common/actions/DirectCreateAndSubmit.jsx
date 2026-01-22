import React, { useEffect } from "react";
import { Button, Message } from "semantic-ui-react";
import PropTypes from "prop-types";
import {
  useRequestContext,
  ConfirmationModal,
  REQUEST_TYPE,
} from "@js/oarepo_requests_common";
import { useConfirmationModal } from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { useCallbackContext, useRequestActionContext } from "../contexts";

// Directly create and submit request without modal
const DirectCreateAndSubmit = ({ requestType, requireConfirmation }) => {
  const { isOpen, close, open } = useConfirmationModal();
  const { actionsLocked, setActionsLocked } = useCallbackContext();
  const { performAction, cleanError, error, loading } =
    useRequestActionContext();
  const { requestButtonsIconsConfig } = useRequestContext();
  const buttonIconProps =
    requestButtonsIconsConfig[requestType.type_id] ||
    requestButtonsIconsConfig?.default;
  const buttonContent =
    requestType?.stateful_name || requestType?.name || requestType?.type_id;
  const handleSubmit = async () => {
    setActionsLocked(true);
    try {
      await performAction("submit");
    } finally {
      setActionsLocked(false);
    }
  };

  const handleClick = () => {
    if (requireConfirmation) {
      open();
    } else {
      handleSubmit();
    }
  };
  useEffect(() => {
    let timeoutId;
    if (error) {
      timeoutId = setTimeout(() => {
        cleanError();
      }, 2500);
    }
    return () => {
      clearTimeout(timeoutId);
    };
  }, [error, cleanError, setActionsLocked]);

  return (
    <React.Fragment>
      <Button
        // applicable requests don't have a status
        className={`requests request-create-button ${requestType?.type_id}`}
        fluid
        title={buttonContent}
        content={buttonContent}
        loading={loading}
        disabled={actionsLocked}
        onClick={() => handleClick()}
        labelPosition="left"
        {...buttonIconProps}
      />
      {error && (
        <Message negative className="rel-mb-1">
          <Message.Header>
            {error.message || i18next.t("Request could not be executed.")}
          </Message.Header>
        </Message>
      )}
      <ConfirmationModal
        requestActionName={REQUEST_TYPE.SUBMIT}
        requestOrRequestType={requestType}
        requestExtraData={requestType}
        onConfirmAction={() => {
          handleSubmit();
        }}
        isOpen={isOpen}
        close={close}
      />
    </React.Fragment>
  );
};

DirectCreateAndSubmit.propTypes = {
  requestType: PropTypes.object,
  requireConfirmation: PropTypes.bool,
  isMutating: PropTypes.number,
};

export { DirectCreateAndSubmit };
