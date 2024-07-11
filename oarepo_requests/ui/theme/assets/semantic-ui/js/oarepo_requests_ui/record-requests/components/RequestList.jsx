import React from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { List, Label } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";

import { RequestModal, RequestModalContent } from ".";
import { mapLinksToActions } from "./actions";
import { useRequestContext } from "../contexts";

/**
 * @typedef {import("../types").Request} Request
 */

/**
 * @param {{ requests: Request[] }} props
 */
export const RequestList = ({ requests }) => {
  const { requestTypes } = useRequestContext();

  return (
    <List link divided size="small">
      {requests.map((request) => {
        const requestType = requestTypes.find(requestType => requestType.type_id === request.type);
        const header = !_isEmpty(request?.title) ? request.title : (!_isEmpty(request?.name) ? request.name : request.type);
        const modalActions = mapLinksToActions(request);
        return (
          <RequestModal
            key={request.id}
            request={request}
            requestType={requestType}
            header={header}
            trigger={
              <List.Item as="a" key={request.id} className="ui request-list-item" role="button">
                <List.Content style={{ position: 'relative' }}>
                  <Label size="mini" className="text-muted" attached='top right'>
                    {request?.status ?? i18next.t("No status")}
                  </Label>
                  <List.Header className="mb-10">{header}</List.Header>
                  <List.Description>
                    <small className="text-muted">{request.description}</small>
                  </List.Description>
                </List.Content>
              </List.Item>
            }
            actions={modalActions}
            ContentComponent={RequestModalContent}
          />
        )
      })}
    </List>
  )
};

RequestList.propTypes = {
  requests: PropTypes.array.isRequired,
};