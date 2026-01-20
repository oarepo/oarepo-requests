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
import { useQuery, useIsMutating } from "@tanstack/react-query";
import { httpApplicationJson } from "@js/oarepo_ui";
import { RequestActionController } from "../RequestActionController";
import { useCallbackContext } from "../contexts";
import { RequestActionController as InvenioRequestsActionController } from "@js/invenio_requests/request/actions/RequestActionController";

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
  const { fetchNewRequests, onAfterAction } = useCallbackContext();
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
    data,
    error: customFieldsLoadingError,
    isLoading,
  } = useQuery(
    ["applicableCustomFields", requestType?.type_id || request?.type],
    () =>
      httpApplicationJson.get(
        `/requests/configs/${requestType?.type_id || request?.type}`
      ),
    {
      enabled: !!(requestType?.type_id || request?.type),
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    }
  );
  const customFields = data?.data?.custom_fields;
  const allowedHtmlAttrs = data?.data?.allowedHtmlAttrs;
  const allowedHtmlTags = data?.data?.allowedHtmlTags;

  const requestTypeProperties = data?.data?.request_type_properties;
  const isMutating = useIsMutating();

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
          size="medium"
        />
        {/* {modalActions.map(({ name, component: ActionComponent }) => (
          <ActionComponent
            key={name}
            request={request}
            requestType={requestType}
            extraData={requestTypeProperties}
            isMutating={isMutating}
          />
        ))} */}
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
