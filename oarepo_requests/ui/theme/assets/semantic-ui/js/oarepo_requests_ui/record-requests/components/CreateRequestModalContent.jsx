import React from "react";
import PropTypes from "prop-types";
import { Form, Divider } from "semantic-ui-react";
import { CustomFields } from "react-invenio-forms";

/**
 * @typedef {import("../../record-requests/types").RequestType} RequestType
 * @typedef {import("formik").FormikConfig} FormikConfig
 */

/** @param {{ requestType: RequestType, customSubmitHandler: (e) => void }} props */
export const CreateRequestModalContent = ({ requestType, customFields }) => {
  const description =
    requestType?.stateful_description || requestType?.description;
  return (
    <>
      {description && <p id="request-modal-desc">{description}</p>}
      {customFields?.ui && (
        <Form id="request-form">
          <CustomFields
            config={customFields?.ui}
            templateLoaders={[
              (widget) => import(`@templates/custom_fields/${widget}.js`),
              (widget) => import(`react-invenio-forms`),
            ]}
            fieldPathPrefix="payload"
          />
          <Divider hidden />
        </Form>
      )}
    </>
  );
};

CreateRequestModalContent.propTypes = {
  requestType: PropTypes.object.isRequired,
  customFields: PropTypes.object,
};
