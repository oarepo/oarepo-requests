import React from "react";
import PropTypes from "prop-types";
import { Form, Divider } from "semantic-ui-react";

export const RequestActionModal = ({ requestType, customFields }) => {
  const description =
    requestType?.stateful_description || requestType?.description;

  return (
    <>
      {description && <p>{description}</p>}
      {customFields?.ui && <Form id="request-action-form" />}
    </>
  );
};

RequestActionModal.propTypes = {
  requestType: PropTypes.object.isRequired,
  customFields: PropTypes.object,
};

export default RequestActionModal;
