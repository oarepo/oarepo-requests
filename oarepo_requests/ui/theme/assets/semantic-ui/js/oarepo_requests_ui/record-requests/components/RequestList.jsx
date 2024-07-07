import React from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { List, Label } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import _has from "lodash/has";

import { RequestModal, RequestModalContent } from ".";
import { mapLinksToActions } from "./actions";
import { useRecordContext } from "../contexts";

/**
 * @typedef {import("../types").Request} Request
 * @typedef {import("../types").RequestTypeEnum} RequestTypeEnum
 */

/**
 * @param {{ requests: Request[] }} props
 */
export const RequestList = ({ requests }) => {
  const { record } = useRecordContext();
  const requestTypes = record?.expanded?.request_types ?? [];

  return (
    <List link divided size="small">
      {requests.map((request) => {
        const requestType = requestTypes?.find(requestType => requestType.type_id === request.type) ?? {};
        const requestModalHeader = !_isEmpty(request?.title) ? request.title : (!_isEmpty(request?.name) ? request.name : request.type);

        const modalActions = mapLinksToActions(request.links?.actions);

        return (
          <RequestModal
            key={request.id}
            request={request}
            requestType={requestType}
            trigger={
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
            header={requestModalHeader}
            actions={modalActions}
            content={
              <RequestModalContent request={request} requestType={requestType} requestModalType="accept" />
            }
          />
        )
      })}
    </List>
  )
};

RequestList.propTypes = {
  requests: PropTypes.array.isRequired,
};