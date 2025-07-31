import React, { useEffect } from "react";
import { Button, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";
import { useFormikContext } from "formik";
import {
  useModalControlContext,
  useAction,
  ConfirmationModal,
  REQUEST_TYPE,
} from "@js/oarepo_requests_common";
import { useConfirmationModal } from "@js/oarepo_ui";

export const RequestActionButton = ({
  requestOrRequestType,
  extraData,
  isMutating,
  iconName,
  action,
  buttonLabel,
  requireConfirmation,
  requestActionName,
  ...uiProps
}) => {
  const formik = useFormikContext();

  const { isOpen, close, open } = useConfirmationModal();

  const modalControl = useModalControlContext();
  const { isLoading, mutate: requestAction } = useAction({
    action,
    requestOrRequestType,
    formik,
    modalControl,
    requestActionName,
  });

  const handleClick = () => {
    if (requireConfirmation) {
      open();
    } else {
      requestAction();
    }
  };

  useEffect(() => {
    if (requestActionName !== REQUEST_TYPE.SUBMIT) return;

    const handleKeyDown = (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        handleClick();
      }
    };

    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
    // want to run this only once when the component mounts
  }, []);

  return (
    <>
      <Button
        title={buttonLabel}
        onClick={handleClick}
        className="requests request-action-button"
        icon
        labelPosition="left"
        loading={isLoading}
        disabled={isMutating > 0}
        {...uiProps}
      >
        <Icon name={iconName} />
        {buttonLabel}
      </Button>
      <ConfirmationModal
        requestActionName={requestActionName}
        requestOrRequestType={requestOrRequestType}
        requestExtraData={extraData}
        onConfirmAction={(comment) => {
          requestAction(comment);
        }}
        isOpen={isOpen}
        close={close}
      />
    </>
  );
};

RequestActionButton.propTypes = {
  requestOrRequestType: PropTypes.object,
  extraData: PropTypes.object,
  isMutating: PropTypes.number,
  iconName: PropTypes.string,
  action: PropTypes.func,
  buttonLabel: PropTypes.string,
  requireConfirmation: PropTypes.bool,
  requestActionName: PropTypes.string,
};

export default RequestActionButton;
