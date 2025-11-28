import React, { useState } from "react";
import { Icon, Button, Popup } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_requests/i18next";
import PropTypes from "prop-types";
import RequestActionModal from "./RequestActionModal";

export const RequestActionButton = ({ disabled = false, requestType }) => {
  const [modalOpen, setModalOpen] = useState(false);
  const handleOpen = () => setModalOpen(true);
  const handleClose = () => setModalOpen(false);

  return (
    <>
      <Popup
        content={i18next.t("You don't have permissions to share this record.")}
        disabled={!disabled}
        trigger={
          <Button
            fluid
            onClick={handleOpen}
            disabled={disabled}
            primary
            size="medium"
            aria-haspopup="dialog"
            icon
            labelPosition="left"
          >
            <Icon name="share square" />
            {i18next.t("Share")}
          </Button>
        }
      />
      <RequestActionModal open={modalOpen} handleClose={handleClose} />
    </>
  );
};

RequestActionButton.propTypes = {
  disabled: PropTypes.bool,
  requestType: PropTypes.object.isRequired,
};

export default RequestActionButton;
