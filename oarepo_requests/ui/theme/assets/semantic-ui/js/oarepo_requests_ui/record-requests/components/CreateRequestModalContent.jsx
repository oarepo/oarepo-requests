import React from "react";
import PropTypes from "prop-types";

import { Segment, Form, Divider } from "semantic-ui-react";
import { useFormikContext } from "formik";

import _isFunction from "lodash/isFunction";

import { CustomFields } from "react-invenio-forms";

/** 
 * @typedef {import("../types").RequestType} RequestType
 * @typedef {import("formik").FormikConfig} FormikConfig
 */

/** @param {{ requestType: RequestType, customSubmitHandler: (e) => void }} props */
export const CreateRequestModalContent = ({ requestType, customSubmitHandler }) => {
  const payloadUI = requestType?.payload_ui;

  const { handleSubmit } = useFormikContext();

  const onSubmit = (event) => {
    if (_isFunction(customSubmitHandler)) {
      customSubmitHandler(event?.nativeEvent?.submitter?.name);
    } else {
      handleSubmit(event);
    }
  }

  return (
    <>
      {requestType?.description &&
        <p id="request-modal-desc">
          {requestType.description}
        </p>
      }
      <Form onSubmit={onSubmit} id="request-form">
        {payloadUI &&
          <Segment basic>
            <CustomFields
              config={payloadUI}
              templateLoaders={[
                (widget) => import(`@templates/custom_fields/${widget}.js`),
                (widget) => import(`react-invenio-forms`)
              ]}
              fieldPathPrefix="payload"
            />
            <Divider hidden />
          </Segment>
        }
      </Form>
    </>
  );
}

CreateRequestModalContent.propTypes = {
  requestType: PropTypes.object.isRequired,
  extraPreSubmitEvent: PropTypes.func
};