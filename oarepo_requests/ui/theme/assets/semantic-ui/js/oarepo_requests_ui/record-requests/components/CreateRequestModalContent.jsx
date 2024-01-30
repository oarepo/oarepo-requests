import React, { useState, useRef, useEffect } from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Dimmer, Loader, Segment, Modal, Button, Header, Icon, Grid, Input, List, Container, Message, Form, Divider } from "semantic-ui-react";
import { useFormikContext } from "formik";

import _isFunction from "lodash/isFunction";

import { CustomFields } from "react-invenio-forms";

/** 
 * @typedef {import("../types").RequestType} RequestType
 * @typedef {import("formik").FormikConfig} FormikConfig
 */

/** @param {{ requestType: RequestType }} props */
export const CreateRequestModalContent = ({ requestType, extraPreSubmitEvent }) => {
  const payloadUI = requestType?.payload_ui;

  const { isSubmitting, isValid, handleSubmit } = useFormikContext();

  const customSubmitHandler = (event) => {
    _isFunction(extraPreSubmitEvent) && extraPreSubmitEvent(event);
    handleSubmit(event);
  }

  return (
    <>
      {requestType?.description &&
        <p id="request-modal-desc">
          {requestType.description}
        </p>
      }
      {payloadUI &&
        <Segment>
          <Form onSubmit={customSubmitHandler} id="request-form">
            <CustomFields
              // ref={cfRef}
              config={payloadUI}
              templateLoaders={[
                (widget) => import(`@templates/custom_fields/${widget}.js`),
                (widget) => import(`react-invenio-forms`)
              ]}
              fieldPathPrefix="payload"
            />
            <Divider hidden />
          </Form>
        </Segment>
      }
    </>
  );
}

CreateRequestModalContent.propTypes = {
  requestType: PropTypes.object.isRequired,
  extraPreSubmitEvent: PropTypes.func
};