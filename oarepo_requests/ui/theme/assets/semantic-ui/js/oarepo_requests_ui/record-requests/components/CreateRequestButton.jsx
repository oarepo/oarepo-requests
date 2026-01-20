import React, { useRef, useState } from "react";
import { Button } from "semantic-ui-react";
import { RequestModal, CreateRequestModalContent } from ".";
import { DirectCreateAndSubmit } from "@js/oarepo_requests_common/actions";
import PropTypes from "prop-types";
import { useCallbackContext } from "../../common";
import { FormikRefContextProvider } from "../../common/contexts/FormikRefContext";

export const CreateRequestButton = ({
  requestType,
  buttonIconProps,
  header,
}) => {
  const { actionsLocked } = useCallbackContext();
  const { dangerous, has_form: hasForm } = requestType;
  const needsDialog = dangerous || hasForm;
  if (!hasForm) {
    return (
      <DirectCreateAndSubmit
        requestType={requestType}
        requireConfirmation={dangerous}
      />
    );
  }

  if (needsDialog) {
    return (
      <FormikRefContextProvider>
        <RequestModal
          requestType={requestType}
          header={header}
          requestCreationModal
          trigger={
            <Button
              className={`requests request-create-button ${requestType.type_id}`}
              fluid
              title={header}
              content={header}
              disabled={actionsLocked}
              labelPosition="left"
              {...buttonIconProps}
            />
          }
          ContentComponent={CreateRequestModalContent}
        />
      </FormikRefContextProvider>
    );
  }

  return null;
};

CreateRequestButton.propTypes = {
  requestType: PropTypes.object,
  isMutating: PropTypes.number.isRequired,
  buttonIconProps: PropTypes.object,
  header: PropTypes.string.isRequired,
};
