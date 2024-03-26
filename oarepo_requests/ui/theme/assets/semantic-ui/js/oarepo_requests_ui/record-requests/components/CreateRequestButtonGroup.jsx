import React, { useState } from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";

import Overridable from "react-overridable";
import { List, Segment, Header, Button } from "semantic-ui-react";

import { RequestModal } from "./RequestModal";

/**
 * @typedef {import("../types").Request} Request
 * @typedef {import("../types").RequestType} RequestType
 */

/**
 * @param {{ requestTypes: RequestType[] }} props
 */
export const CreateRequestButtonGroup = ({ requestTypes }) => {
  const createRequests = requestTypes.filter(requestType => requestType.links.actions?.create);

  return (
    <Segment>
      <Header size="small" className="detail-sidebar-header">{i18next.t("Create Request")}</Header>
      <Button.Group vertical compact fluid basic>
        {createRequests.map((requestType) => (
          <RequestModal 
            key={requestType.type_id} 
            request={requestType} 
            requestModalType="create" 
            triggerButton={<Button icon="plus" title={i18next.t(requestType.name)} basic compact content={requestType.name} />} 
          />
        ))}
      </Button.Group>
    </Segment>
  );
}