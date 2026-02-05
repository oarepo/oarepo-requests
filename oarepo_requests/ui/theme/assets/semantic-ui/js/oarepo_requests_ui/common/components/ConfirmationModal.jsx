import React, { useState } from "react";
import { Modal, Message, Icon, Divider } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import PropTypes from "prop-types";
import { RichEditor } from "react-invenio-forms";
import { useRequestActionContext } from "../contexts";
import { ConfirmationModalConfirmButton } from "./ConfirmationModalConfirmButton";
import { ConfirmationModalCancelButton } from "./ConfirmationModalCancelButton";
import { REQUEST_TYPE } from "../utils/objects";

const ACTION_HEADERS = {
  [REQUEST_TYPE.CREATE]: i18next.t("Create request"),
  [REQUEST_TYPE.SUBMIT]: i18next.t("Submit request"),
  [REQUEST_TYPE.CANCEL]: i18next.t("Cancel request"),
  [REQUEST_TYPE.ACCEPT]: i18next.t("Accept request"),
  [REQUEST_TYPE.DECLINE]: i18next.t("Decline request"),
};

export const ConfirmationModal = ({
  requestActionName,
  requestOrRequestType,
  requestExtraData,
  isOpen,
  close,
  onConfirmAction,
}) => {
  const [comment, setComment] = useState("");
  const handleChange = (event, value) => {
    setComment(value);
  };
  const { loading } = useRequestActionContext();
  const dangerous = requestExtraData?.dangerous;
  // TODO: this is primitive and probably the best way would be to have a config in the request type on BE
  // that would say which actions should offer you the comment input
  const isDecline = requestActionName === REQUEST_TYPE.DECLINE;
  const handleConfirmAction = (requestActionName, comment) => {
    onConfirmAction(requestActionName, comment);
    setComment("");
    close();
  };
  const isCreateOrSubmit =
    requestActionName === REQUEST_TYPE.CREATE ||
    requestActionName === REQUEST_TYPE.SUBMIT;
  const isAccept = requestActionName === REQUEST_TYPE.ACCEPT;
  return (
    <Modal
      open={isOpen}
      className="requests dangerous-action-confirmation-modal"
    >
      <Modal.Header>{`${ACTION_HEADERS[requestActionName]} (${requestOrRequestType.name})`}</Modal.Header>
      <Modal.Content>
        {isCreateOrSubmit && (
          <Message negative>
            <Message.Header>
              {i18next.t(
                "Are you sure you wish to proceed? After this request is accepted, it will not be possible to reverse the action.",
              )}
            </Message.Header>
          </Message>
        )}
        {isDecline && (
          <>
            {i18next.t("Add comment (optional)")}
            <Divider hidden />
            <RichEditor
              inputValue={() => comment}
              onChange={handleChange}
              editorConfig={{
                auto_focus: true,
                min_height: 100,
              }}
            />
          </>
        )}
        {requestActionName === REQUEST_TYPE.DECLINE && (
          <Message>
            <Icon name="info circle" className="text size large" />
            <span>
              {i18next.t(
                "It is highly recommended to provide an explanation for the rejection of the request. Note that it is always possible to provide explanation later on the request timeline.",
              )}
            </span>
          </Message>
        )}
      </Modal.Content>
      <Modal.Actions className="flex justify-space-between align-items-center">
        <ConfirmationModalCancelButton onClick={close} />
        {isAccept ? (
          <ConfirmationModalConfirmButton
            positive={!dangerous}
            negative={dangerous}
            onClick={() => handleConfirmAction(requestActionName, comment)}
            content={i18next.t("Proceed")}
            loading={loading}
          />
        ) : (
          <ConfirmationModalConfirmButton
            negative
            onClick={() => handleConfirmAction(requestActionName, comment)}
            content={i18next.t("Proceed")}
            loading={loading}
          />
        )}
      </Modal.Actions>
    </Modal>
  );
};

ConfirmationModal.propTypes = {
  requestActionName: PropTypes.string,
  requestOrRequestType: PropTypes.object,
  requestExtraData: PropTypes.object,
  isOpen: PropTypes.bool,
  close: PropTypes.func,
  onConfirmAction: PropTypes.func,
};
