import React from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { List, Label } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import _has from "lodash/has";
import { Formik } from "formik";

import { SubmitModal, AcceptDeclineCancelModal, ViewOnlyModal } from ".";
import { mapPayloadUiToInitialValues } from "../utils";

/**
 * @typedef {import("../types").Request} Request
 * @typedef {import("../types").RequestTypeEnum} RequestTypeEnum
 */

/**
 * @param {{ requests: Request[], requestModalType: RequestTypeEnum }} props
 */
export const RequestList = ({ requests, requestTypes, requestModalType }) => {
  return (
    <List link divided size="small">
      {requests.map((request) => {
        const requestType = requestTypes?.find(requestType => requestType.type_id === request.type) ?? {};
        const requestModalHeader = !_isEmpty(request?.title) ? request.title : (!_isEmpty(request?.name) ? request.name : request.type);

        let ModalComponent = requestModalType === "accept" ? AcceptDeclineCancelModal : ViewOnlyModal;
        if (_has(request, "links.actions")) {
          if ("submit" in request.links.actions) {
            ModalComponent = SubmitModal;
          } else if ("cancel" in request.links.actions) {
            ModalComponent = AcceptDeclineCancelModal;
          } else if (_isEmpty(request.links.actions)) {
            ModalComponent = ViewOnlyModal;
          }
        }

        return (
          <Formik
            key={request.id}
            initialValues={
              !_isEmpty(request?.payload) ? 
                { payload: request.payload } : 
                (request?.payload_ui ? mapPayloadUiToInitialValues(request?.payload_ui) : {})
            }
            onSubmit={() => { }} // We'll redefine with customSubmitHandler
          >
            <ModalComponent
              key={request.id}
              request={request}
              requestType={requestType}
              triggerElement={
                <List.Item as="a" key={request.id} className="ui request-list-item" role="button">
                  <List.Content style={{ position: 'relative' }}>
                    <Label size="mini" className="text-muted" attached='top right'>
                      {request?.status ?? i18next.t("No status")}
                    </Label>
                    <List.Header className="mb-10">{!_isEmpty(request?.title) ? request.title : (!_isEmpty(request?.name) ? request.name : request.type)}</List.Header>
                    <List.Description>
                      <small className="text-muted">{request.description}</small>
                    </List.Description>
                  </List.Content>
                </List.Item>
              }
              modalHeader={requestModalHeader}
            />
          </Formik>
        )
      })}
    </List>
  )
};

RequestList.propTypes = {
  requests: PropTypes.array.isRequired,
  requestTypes: PropTypes.array.isRequired,
  requestModalType: PropTypes.oneOf(["create", "accept", "submit", "cancel"]),
  fetchNewRequests: PropTypes.func,
};