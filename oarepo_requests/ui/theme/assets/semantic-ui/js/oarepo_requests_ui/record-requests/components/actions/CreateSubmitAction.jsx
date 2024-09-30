import React from "react";
import { Button } from "semantic-ui-react";
import { useRequestsApi } from "../../utils/hooks";
import PropTypes from "prop-types";
import { useRequestContext } from "../../contexts";

// Directly create and submit request without modal
const CreateSubmitAction = ({ requestType }) => {
  const { createAndSubmitRequest } = useRequestsApi(requestType);
  const { isLoading, mutate } = createAndSubmitRequest;
  const { requestButtonsIconsConfig } = useRequestContext();
  const buttonIconProps = requestButtonsIconsConfig[requestType.type_id];
  const buttonContent =
    requestType?.stateful_name || requestType?.name || requestType?.type_id;
  return (
    <Button
      // applicable requests don't have a status
      className={`requests request-create-button ${requestType?.type_id}`}
      fluid
      title={buttonContent}
      content={buttonContent}
      loading={isLoading}
      onClick={() => mutate()}
      {...buttonIconProps}
    />
  );
};

CreateSubmitAction.propTypes = {
  requestType: PropTypes.object,
};

export default CreateSubmitAction;
