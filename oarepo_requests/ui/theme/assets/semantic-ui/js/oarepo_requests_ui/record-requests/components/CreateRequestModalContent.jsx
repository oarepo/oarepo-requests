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

/** @param {{ requestType: RequestType, customSubmitHandler: (e) => void }} props */
export const CreateRequestModalContent = ({ requestType, onCompletedAction }) => {  
  const { doAction, doCreateAndSubmitAction } = useRequestsApi(requestType, onCompletedAction);
  const { submitForm, setErrors, setSubmitting } = useFormikContext();

  const payloadUI = requestType?.payload_ui;

  const onFormSubmit = async (event) => {
    event.preventDefault();
    const submitButtonName = event?.nativeEvent?.submitter?.name;
    try {
      await submitForm();
      if (submitButtonName === "create-and-submit-request") {
        doCreateAndSubmitAction(!_isEmpty(payloadUI));
        return;
      }
      doAction(REQUEST_TYPE.CREATE);
    } catch (error) {
      setErrors({ api: error });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      {requestType?.description &&
        <p id="request-modal-desc">
          {requestType.description}
        </p>
      }
      {payloadUI &&
        <Form onSubmit={onFormSubmit} id="request-form">
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
        </Form>
      }
    </>
  );
}

CreateRequestModalContent.propTypes = {
  requestType: PropTypes.object.isRequired,
  extraPreSubmitEvent: PropTypes.func
};