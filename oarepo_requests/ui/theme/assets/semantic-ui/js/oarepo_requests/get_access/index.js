// Copyright (c) 2026 CESNET
// SPDX-License-Identifier: MIT

// Components for requesting membership in a group ("get access" to the repository).
//
// - GetAccessButton: a button that, when clicked, opens GetAccessModal. This
//   is the component consuming apps should use.
// - GetAccessModal: the modal with the request form itself. Exported mainly
//   so it can be tested/reused directly; normally you don't need it.
//
// Both take `groupId` (the technical group/role identifier used in the
// request payload, e.g. "submitters") and `groupName` (the human-readable
// name shown to the user in the form) as required props. This module does
// not mount itself - consuming apps import GetAccessButton and render it
// into their own page, e.g.:
//
//   import React from "react";
//   import ReactDOM from "react-dom";
//   import { GetAccessButton } from "@js/oarepo_requests/get_access";
//   import { i18next } from "@translations/i18next";
//
//   const domContainer = document.getElementById("standalone_submitter_application");
//   if (domContainer) {
//     ReactDOM.render(
//       <GetAccessButton groupId="submitters" groupName={i18next.t("Submitters")} />,
//       domContainer
//     );
//   }

import React, { useState } from "react";
import PropTypes from "prop-types";
import { Formik } from "formik";
import { Button, Form, Message, Modal } from "semantic-ui-react";
import { TextAreaField, http } from "react-invenio-forms";
import { i18next } from "@translations/oarepo_requests_ui/i18next";

const buildRequestPayload = (reason, groupId) => ({
  request_type: "group_membership",
  topic: { group: groupId },
  payload: { justification: reason },
});

export const GetAccessModal = ({ isOpen, onClose, groupId, groupName }) => {
  const [isSubmitted, setSubmitted] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const handleSubmit = async (values, { setSubmitting }) => {
    setSubmitting(true);
    setErrorMsg("");
    try {
      const createResp = await http.post(
        "/api/requests",
        buildRequestPayload(values.reason, groupId)
      );
      const submitLink = createResp.data?.links?.actions?.submit;
      if (submitLink) {
        await http.post(submitLink, {});
        setSubmitted(true);
      } else {
        setErrorMsg(i18next.t("No submit link found."));
      }
    } catch (error) {
      setErrorMsg(
        error?.response?.data?.message ||
          i18next.t("Something went wrong while submitting your request.")
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Formik initialValues={{ reason: "" }} onSubmit={handleSubmit}>
      {({ values, isSubmitting, handleSubmit: submitForm }) => (
        <Modal
          open={isOpen}
          onClose={onClose}
          size="small"
          closeIcon
          closeOnDimmerClick={false}
        >
          <Modal.Header>{i18next.t("Apply for Write Access")}</Modal.Header>
          <Modal.Content>
            {isSubmitted ? (
              <Message positive>
                <Message.Header>
                  {i18next.t("Request submitted")}
                </Message.Header>
                <p>
                  {i18next.t(
                    "Your request for standalone submitter access has been submitted. Please wait for it to be reviewed - you will receive an email notification once it has been processed."
                  )}
                </p>
              </Message>
            ) : (
              <>
                <Message hidden={errorMsg === ""} negative>
                  <strong>{errorMsg}</strong>
                </Message>
                <p>
                  {i18next.t(
                    'Please describe how you intend to use your membership in the group "{{groupName}}".',
                    { groupName }
                  )}
                </p>
                <Form>
                  <TextAreaField
                    fieldPath="reason"
                    label={i18next.t("Intended use")}
                  />
                </Form>
              </>
            )}
          </Modal.Content>
          <Modal.Actions>
            {isSubmitted ? (
              <Button primary onClick={onClose} content={i18next.t("Close")} />
            ) : (
              <>
                <Button
                  onClick={onClose}
                  floated="left"
                  disabled={isSubmitting}
                  content={i18next.t("Cancel")}
                />
                <Button
                  positive
                  loading={isSubmitting}
                  disabled={isSubmitting || !values.reason}
                  onClick={submitForm}
                  content={i18next.t("Apply for Write Access")}
                />
              </>
            )}
          </Modal.Actions>
        </Modal>
      )}
    </Formik>
  );
};

GetAccessModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  groupId: PropTypes.string.isRequired,
  groupName: PropTypes.string.isRequired,
};

export const GetAccessButton = ({ groupId, groupName }) => {
  const [isModalOpen, setModalOpen] = useState(false);

  return (
    <>
      <Button
        positive
        content={i18next.t("Apply for Write Access")}
        onClick={() => setModalOpen(true)}
      />
      {isModalOpen && (
        <GetAccessModal
          isOpen={isModalOpen}
          onClose={() => setModalOpen(false)}
          groupId={groupId}
          groupName={groupName}
        />
      )}
    </>
  );
};

GetAccessButton.propTypes = {
  groupId: PropTypes.string.isRequired,
  groupName: PropTypes.string.isRequired,
};
