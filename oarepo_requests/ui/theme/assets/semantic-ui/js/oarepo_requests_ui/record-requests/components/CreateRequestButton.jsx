import React from "react";
import { Button } from "semantic-ui-react";
import { RequestModal, CreateRequestModalContent } from ".";
import { DirectCreateAndSubmit } from "@js/oarepo_requests_common/actions";
import PropTypes from "prop-types";
import { useCallbackContext } from "../../common";
import { FormikRefContextProvider } from "../../common/contexts/FormikRefContext";
import { RequestActionController } from "../../common";

export const CreateRequestButton = ({
  requestType,
  buttonIconProps,
  header,
}) => {
  const {
    actionsLocked,
    fetchNewRequests,
    onAfterAction,
    onBeforeAction,
    onErrorPlugins,
  } = useCallbackContext();
  const { dangerous, has_form: hasForm } = requestType;
  const needsDialog = dangerous || hasForm;
  const actionSuccessCallback = (response) => {
    const redirectionURL =
      response?.data?.links?.ui_redirect_url ||
      response?.data?.links?.topic?.self_html;
    fetchNewRequests();

    if (redirectionURL) {
      window.location.href = redirectionURL;
    }
  };
  if (!hasForm) {
    return (
      <RequestActionController
        key={requestType.type_id}
        renderAllActions={false}
        request={requestType}
        actionSuccessCallback={onAfterAction ?? actionSuccessCallback}
        onBeforeAction={onBeforeAction}
        onErrorPlugins={onErrorPlugins}
      >
        <DirectCreateAndSubmit
          requestType={requestType}
          requireConfirmation={dangerous}
        />
      </RequestActionController>
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
