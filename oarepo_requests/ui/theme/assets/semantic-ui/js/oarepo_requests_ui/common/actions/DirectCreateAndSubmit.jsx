import React, { useEffect } from "react";
import { Button, Message } from "semantic-ui-react";
import PropTypes from "prop-types";
import {
  useAction,
  useRequestContext,
  saveAndSubmit,
  ConfirmationModal,
  REQUEST_TYPE,
} from "@js/oarepo_requests_common";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { useConfirmationModal } from "@js/oarepo_ui";

// Directly create and submit request without modal
const DirectCreateAndSubmit = ({
  requestType,
  requireConfirmation,
  isMutating,
}) => {
  const { isOpen, close, open } = useConfirmationModal();

  const {
    isLoading,
    mutate: createAndSubmit,
    isError,
    error,
    reset,
  } = useAction({
    action: saveAndSubmit,
    requestOrRequestType: requestType,
  });
  const { requestButtonsIconsConfig } = useRequestContext();
  const buttonIconProps = requestButtonsIconsConfig[requestType.type_id];
  const buttonContent =
    requestType?.stateful_name || requestType?.name || requestType?.type_id;

  const handleClick = () => {
    if (requireConfirmation) {
      open();
    } else {
      createAndSubmit();
    }
  };
  useEffect(() => {
    if (isError) {
      setTimeout(() => {
        reset();
      }, 2500);
    }
    return () => isError && reset();
  }, [isError, reset]);

  return (
    <React.Fragment>
      <Button
        // applicable requests don't have a status
        className={`requests request-create-button ${requestType?.type_id}`}
        fluid
        title={buttonContent}
        content={buttonContent}
        loading={isLoading}
        disabled={isMutating > 0}
        onClick={() => handleClick()}
        {...buttonIconProps}
      />
      {isError && (
        <Message negative>
          <Message.Header>
            {error?.response?.data?.errors?.length > 0
              ? i18next.t(
                  "Record has validation errors. Redirecting to form..."
                )
              : i18next.t(
                  "Request not created successfully. Please try again in a moment."
                )}
          </Message.Header>
        </Message>
      )}
      <ConfirmationModal
        requestActionName={REQUEST_TYPE.SUBMIT}
        requestOrRequestType={requestType}
        requestExtraData={requestType}
        onConfirmAction={() => {
          createAndSubmit();
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

export default DirectCreateAndSubmit;
