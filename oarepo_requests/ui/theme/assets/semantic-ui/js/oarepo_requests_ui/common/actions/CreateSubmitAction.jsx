import React, { useEffect } from "react";
import { Button } from "semantic-ui-react";
import PropTypes from "prop-types";
import {
  useAction,
  useRequestContext,
  saveAndSubmit,
  useConfirmModalContext,
  REQUEST_TYPE,
  WarningMessage,
} from "@js/oarepo_requests_common";
import { i18next } from "@translations/oarepo_requests_ui/i18next";

// Directly create and submit request without modal
const CreateSubmitAction = ({ requestType, requireConfirmation }) => {
  const { confirmAction } = useConfirmModalContext();
  const { hasForm, dangerous, editable } = requestType;
  const {
    isLoading,
    mutate: createAndSubmit,
    isError,
    reset,
  } = useAction({
    action: saveAndSubmit,
    requestOrRequestType: requestType,
    confirmAction,
  });
  const { requestButtonsIconsConfig } = useRequestContext();
  const buttonIconProps = requestButtonsIconsConfig[requestType.type_id];
  const buttonContent =
    requestType?.stateful_name || requestType?.name || requestType?.type_id;

  const handleClick = () => {
    if (requireConfirmation) {
      confirmAction(() => createAndSubmit(), REQUEST_TYPE.CREATE, {
        hasForm,
        dangerous,
        editable,
      });
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
        onClick={() => handleClick()}
        {...buttonIconProps}
      />
      {isError && (
        <WarningMessage
          message={i18next.t(
            "Request not created successfully. Please try again in a moment."
          )}
        />
      )}
    </React.Fragment>
  );
};

CreateSubmitAction.propTypes = {
  requestType: PropTypes.object,
  requireConfirmation: PropTypes.bool,
};

export default CreateSubmitAction;
