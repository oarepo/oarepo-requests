import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import {
  Dimmer,
  Loader,
  Modal,
  Button,
  Icon,
  Message,
} from "semantic-ui-react";
import { useFormikContext } from "formik";
import PropTypes from "prop-types";
import { RequestActionController } from "../RequestActionController";
import { useCallbackContext, useRequestConfigContext } from "../contexts";

export const RequestModalContentAndActions = ({
  request,
  requestType,
  onSubmit,
  ContentComponent,
  requestCreationModal,
  onClose,
  formikRef,
}) => {
  const { errors } = useFormikContext();
  const error = errors?.api;
  const { fetchNewRequests, onAfterAction, onBeforeAction } =
    useCallbackContext();
  const actionSuccessCallback = (response) => {
    const redirectionURL =
      response?.data?.links?.ui_redirect_url ||
      response?.data?.links?.topic?.self_html;
    fetchNewRequests();

    if (redirectionURL) {
      window.location.href = redirectionURL;
    }
  };
  const {
    requestTypeConfig,
    isLoading,
    error: customFieldsLoadingError,
  } = useRequestConfigContext();

  const customFields = requestTypeConfig?.custom_fields;
  const allowedHtmlAttrs = requestTypeConfig?.allowedHtmlAttrs;
  const allowedHtmlTags = requestTypeConfig?.allowedHtmlTags;

  return (
    <React.Fragment>
      <Dimmer active={isLoading}>
        <Loader inverted />
      </Dimmer>
      <Modal.Content>
        {error && (
          <Message negative>
            <Message.Header>{error}</Message.Header>
          </Message>
        )}
        {customFieldsLoadingError && (
          <Message negative>
            <Message.Header>
              {i18next.t("Form fields could not be fetched.")}
            </Message.Header>
          </Message>
        )}
        <ContentComponent
          request={request}
          requestType={requestType}
          onCompletedAction={onSubmit}
          customFields={customFields}
          allowedHtmlAttrs={allowedHtmlAttrs}
          allowedHtmlTags={allowedHtmlTags}
        />
      </Modal.Content>
      <Modal.Actions className="flex justify-space-between align-items-center">
        <Button onClick={onClose} icon labelPosition="left">
          <Icon name="cancel" />
          {i18next.t("Close")}
        </Button>
        <RequestActionController
          request={requestCreationModal ? requestType : request}
          actionSuccessCallback={onAfterAction ?? actionSuccessCallback}
          formikRef={formikRef}
          onBeforeAction={onBeforeAction}
          size="medium"
        />
      </Modal.Actions>
    </React.Fragment>
  );
};

RequestModalContentAndActions.propTypes = {
  request: PropTypes.object,
  requestType: PropTypes.object,
  ContentComponent: PropTypes.func,
  requestCreationModal: PropTypes.bool,
  onSubmit: PropTypes.func,
  onClose: PropTypes.func,
  formikRef: PropTypes.object,
};
