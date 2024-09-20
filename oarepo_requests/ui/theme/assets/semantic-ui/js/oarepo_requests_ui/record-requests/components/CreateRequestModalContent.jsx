import React from "react";
import PropTypes from "prop-types";

import { Segment, Form, Divider } from "semantic-ui-react";
import { useFormikContext } from "formik";

import _isEmpty from "lodash/isEmpty";
import { CustomFields } from "react-invenio-forms";

import { REQUEST_TYPE } from "../utils/objects";
import { useRequestsApi } from "../utils/hooks";

/**
 * @typedef {import("../types").RequestType} RequestType
 * @typedef {import("formik").FormikConfig} FormikConfig
 */
const FormikStateLogger = ({ values, errors }) => (
  <>
    <pre>{JSON.stringify(values, null, 2)}</pre>
    <pre>{JSON.stringify(errors, null, 2)}</pre>
  </>
);
/** @param {{ requestType: RequestType, customSubmitHandler: (e) => void }} props */
export const CreateRequestModalContent = ({
  requestType,
  onCompletedAction,
  customFields,
}) => {
  const { values, errors } = useFormikContext();

  return (
    <>
      {requestType?.description && (
        <p id="request-modal-desc">{requestType.description}</p>
      )}
      {customFields?.ui && (
        <Form id="request-form">
          <Segment basic>
            <CustomFields
              config={customFields?.ui}
              templateLoaders={[
                (widget) => import(`@templates/custom_fields/${widget}.js`),
                (widget) => import(`react-invenio-forms`),
              ]}
              fieldPathPrefix="payload"
            />
            <FormikStateLogger values={values} errors={errors} />
            <Divider hidden />
          </Segment>
        </Form>
      )}
    </>
  );
};

CreateRequestModalContent.propTypes = {
  requestType: PropTypes.object.isRequired,
  extraPreSubmitEvent: PropTypes.func,
};
