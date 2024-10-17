import React from "react";
import { useConfirmationModal } from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import {
  Dimmer,
  Loader,
  Modal,
  Button,
  Icon,
  Confirm,
  Message,
} from "semantic-ui-react";
import { useFormik, FormikProvider, useFormikContext } from "formik";
import _isEmpty from "lodash/isEmpty";
import {
  ModalControlContextProvider,
  mapLinksToActions,
  ConfirmModalContextProvider,
} from "@js/oarepo_requests_common";
import PropTypes from "prop-types";
import { useQuery, useIsMutating } from "@tanstack/react-query";
// TODO: remove when /configs starts using vnd zenodo accept header
import { http } from "react-invenio-forms";

/**
 * @typedef {import("../../record-requests/types").Request} Request
 * @typedef {import("../../record-requests/types").RequestType} RequestType
 * @typedef {import("react").ReactElement} ReactElement
 */

/** @param {{ request: Request?, requestType: RequestType?, header: string | ReactElement, trigger: ReactElement, ContentComponent: ReactElement, requestCreationModal: Boolean }} props */

export const RequestModal = ({
  request,
  requestType,
  header,
  trigger,
  ContentComponent,
  requestCreationModal,
}) => {
  const { isOpen, close: closeModal, open: openModal } = useConfirmationModal();

  const formik = useFormik({
    initialValues: !_isEmpty(request?.payload)
      ? { payload: request.payload }
      : { payload: {} },
  });
  const { resetForm, setErrors } = formik;

  const isMutating = useIsMutating();

  const onClose = () => {
    closeModal();
    setErrors({});
    resetForm();
  };
  return (
    <FormikProvider value={formik}>
      <ModalControlContextProvider
        value={{
          isOpen,
          closeModal: onClose,
          openModal,
        }}
      >
        <ConfirmModalContextProvider
          requestOrRequestType={requestCreationModal ? requestType : request}
        >
          {({ confirmDialogProps }) => (
            <React.Fragment>
              <Modal
                className="requests-request-modal"
                as={Dimmer.Dimmable}
                blurring
                onClose={onClose}
                onOpen={openModal}
                open={isOpen}
                trigger={trigger || <Button content="Open Modal" />}
                closeIcon
                closeOnDocumentClick={false}
                closeOnDimmerClick={false}
                aria-labelledby="request-modal-header"
                aria-describedby="request-modal-desc"
              >
                <Dimmer active={isMutating > 0}>
                  <Loader inverted size="large" />
                </Dimmer>
                <Modal.Header as="h1" id="request-modal-header">
                  {header}
                </Modal.Header>
                <RequestModalContentAndActions
                  request={request}
                  requestType={requestType}
                  ContentComponent={ContentComponent}
                  requestCreationModal={requestCreationModal}
                  isMutating={isMutating}
                />
              </Modal>
              <Confirm {...confirmDialogProps} />
            </React.Fragment>
          )}
        </ConfirmModalContextProvider>
      </ModalControlContextProvider>
    </FormikProvider>
  );
};

RequestModal.propTypes = {
  request: PropTypes.object,
  requestType: PropTypes.object,
  header: PropTypes.oneOfType([PropTypes.string, PropTypes.element]),
  trigger: PropTypes.element,
  ContentComponent: PropTypes.func,
  requestCreationModal: PropTypes.bool,
};

const RequestModalContentAndActions = ({
  request,
  requestType,
  onSubmit,
  ContentComponent,
  requestCreationModal,
  onClose,
}) => {
  const { errors } = useFormikContext();
  const error = errors?.api;

  const {
    data,
    error: customFieldsLoadingError,
    isLoading,
  } = useQuery(
    ["applicableCustomFields", requestType?.type_id || request?.type],
    () =>
      http.get(`/requests/configs/${requestType?.type_id || request?.type}`),
    {
      enabled: !!(requestType?.type_id || request?.type),
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    }
  );
  const customFields = data?.data?.custom_fields;
  const requestTypeProperties = data?.data?.request_type_properties;
  const isMutating = useIsMutating();
  const modalActions = mapLinksToActions(
    requestCreationModal ? requestType : request,
    customFields,
    requestTypeProperties
  );

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
          modalActions={modalActions}
        />
      </Modal.Content>
      <Modal.Actions>
        {modalActions.map(({ name, component: ActionComponent }) => (
          <ActionComponent
            key={name}
            request={request}
            requestType={requestType}
            extraData={requestTypeProperties}
            isMutating={isMutating}
          />
        ))}
        <Button onClick={onClose} icon labelPosition="left">
          <Icon name="cancel" />
          {i18next.t("Close")}
        </Button>
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
};
