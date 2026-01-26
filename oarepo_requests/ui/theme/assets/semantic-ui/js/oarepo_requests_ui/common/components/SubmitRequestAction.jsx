import React from "react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import { Modal } from "semantic-ui-react";
import { useRequestActionContext } from "../contexts";
import { RequestActionModalTrigger } from "@js/invenio_requests/request/actions/RequestActionModalTrigger";
import { RequestActionButton } from "@js/invenio_requests/request/actions/RequestActionButton";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { RequestActionModal } from "../RequestActionModal";

export const SubmitRequestAction = ({
  action,
  loading,
  performAction,
  size,
  requestType,
  toggleModal,
  modalOpen,
  handleActionClick,
  modalId,
}) => {
  const { request } = useRequestActionContext();
  if (!request?.dangerous) {
    console.log("rendering button");
    return (
      <RequestActionButton
        action={action}
        handleActionClick={handleActionClick}
        loading={loading}
        size={size}
        requestType={requestType}
      />
    );
  }

  return (
    <React.Fragment>
      <RequestActionModalTrigger
        action={action}
        loading={loading}
        toggleModal={toggleModal}
        modalOpen={modalOpen}
        requestType={requestType}
        size={size}
      />

      <RequestActionModal
        action={action}
        handleActionClick={handleActionClick}
        modalId={modalId}
        requestType={requestType}
      >
        <Modal.Content />
      </RequestActionModal>
    </React.Fragment>
  );
};
