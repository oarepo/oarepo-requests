import React from "react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import { Modal } from "semantic-ui-react";
import { useRequestActionContext } from "../contexts";
import { RequestActionModal } from "@js/invenio_requests/request/actions/RequestActionModal";
import { RequestActionModalTrigger } from "@js/invenio_requests/request/actions/RequestActionModalTrigger";
import { RequestActionButton } from "@js/invenio_requests/request/actions/RequestActionButton";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
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
  console.log("dwadwadwadwadwada");
  const { request } = useRequestActionContext();
  if (!request?.dangerous) {
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
        <Modal.Content>
          {error && (
            <Message negative>
              <p>{error}</p>
            </Message>
          )}
          <Modal.Description>
            {i18next.t("Add comment (optional)")}
            <Divider hidden />
            <RichEditor
              inputValue={() => actionComment}
              onChange={this.onCommentChange}
            />
          </Modal.Description>
        </Modal.Content>
      </RequestActionModal>
    </React.Fragment>
  );
};
