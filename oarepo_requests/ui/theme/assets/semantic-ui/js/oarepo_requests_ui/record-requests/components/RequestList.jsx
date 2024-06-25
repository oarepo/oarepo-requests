import React from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { List, Label } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import _has from "lodash/has";

import { RequestModal } from ".";
import { SubmitModal } from ".";

/**
 * @typedef {import("../types").Request} Request
 * @typedef {import("../types").RequestTypeEnum} RequestTypeEnum
 */

/**
 * @param {{ requests: Request[], requestModalType: RequestTypeEnum }} props
 */
export const RequestList = ({ requests, requestTypes, requestModalType, fetchNewRequests }) => {
  return (
    <List link divided size="small">
      {requests.map((request) => {
        const requestType = requestTypes?.find(requestType => requestType.type_id === request.type) ?? {};
        let modalType = requestModalType;
        let ModalComponent = RequestModal;
        if (_isEmpty(requestModalType) && _has(request, "links.actions")) {
          if ("submit" in request.links.actions) {
            modalType = "submit";
            ModalComponent = SubmitModal;
          } else if ("cancel" in request.links.actions) {
            modalType = "cancel";
          } else if (_isEmpty(request.links.actions)) {
            modalType = "view_only";
          } else {
            modalType = "submit";
            ModalComponent = SubmitModal;
          }
        }
        return (
          <ModalComponent 
            key={request.id} 
            request={request} 
            requestType={requestType} 
            requestTypes={requestTypes} 
            requestModalType={modalType}
            triggerButton={
              <List.Item as="a" key={request.id} className="ui request-list-item" role="button">
                  <List.Content style={{position: 'relative'}}>
                    <Label size="mini" className="text-muted"  attached='top right'>
                      {request?.status ?? i18next.t("No status")}
                    </Label>
                    <List.Header className="mb-10">{!_isEmpty(request?.title) ? request.title : (!_isEmpty(request?.name) ? request.name : request.type)}</List.Header>
                    <List.Description><small className="text-muted">{request.description}</small></List.Description>
                  </List.Content>
              </List.Item>
            }
            fetchNewRequests={fetchNewRequests}
          />
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