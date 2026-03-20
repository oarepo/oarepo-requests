// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
// Copyright (C) 2024 KTH Royal Institute of Technology.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { RequestLinksExtractor } from "@js/invenio_requests/api";
import React from "react";
import Overridable from "react-overridable";
import { Dropdown } from "semantic-ui-react";
import PropTypes from "prop-types";
import { RequestActionButton } from ".";
import { useRequestConfigContext } from "../contexts";
import { REQUEST_TYPE } from "@js/oarepo_requests_common";

const iconConfig = {
  create: "plus",
  submit: "send",
  save: "save",
  cancel: "cancel",
  accept: "checkmark",
  decline: "cancel",
};

const requireConfirmation = (actionName, requestTypesConfig) => {
  if (
    actionName === REQUEST_TYPE.CREATE ||
    actionName === REQUEST_TYPE.CANCEL
  ) {
    return false;
  }
  if (actionName === REQUEST_TYPE.DECLINE) {
    return true;
  }

  return requestTypesConfig?.dangerous || false;
};

const getAvailableActions = (initialActions, requestTypesConfig) => {
  const isEditable = requestTypesConfig?.request_type_properties?.editable;
  const hasCreate = initialActions.includes("create");

  const actions = new Set(initialActions);

  if (!isEditable) {
    actions.delete("create");
  }
  if (hasCreate) {
    actions.add("submit");
  }
  if (isEditable) {
    actions.add("save");
  }

  return [...actions];
};
export const RequestActions = ({ request, size }) => {
  const { requestTypeConfig } = useRequestConfigContext();

  const actions = Object.keys(new RequestLinksExtractor(request).actions);
  const actionNames = getAvailableActions(
    actions,
    requestTypeConfig?.request_type_properties,
  );
  return (
    <Overridable
      id="InvenioRequests.RequestActions.layout"
      request={request}
      actionNames={actionNames}
    >
      <React.Fragment>
        <div className="computer tablet only flex">
          {actionNames.map((actionName) => (
            <RequestActionButton
              requestActionName={actionName}
              key={actionName}
              requestOrRequestType={request}
              extraData={requestTypeConfig?.request_type_properties}
              buttonLabel={requestTypeConfig?.action_labels?.[actionName]}
              iconName={iconConfig[actionName]}
              requireConfirmation={requireConfirmation(
                actionName,
                requestTypeConfig?.request_type_properties,
              )}
              className={`requests request-action-button ${actionName} ${
                requestTypeConfig?.request_type_properties?.dangerous &&
                "dangerous"
              }`}
            />
          ))}
        </div>
        <Dropdown
          text="Actions"
          icon="caret down"
          floating
          labeled
          button
          className="icon mobile only requests request-actions-dropdown"
        >
          <Dropdown.Menu>
            {actionNames.map((actionName) => {
              return (
                <RequestActionButton
                  requestActionName={actionName}
                  key={actionName}
                  requestOrRequestType={request}
                  extraData={requestTypeConfig?.request_type_properties}
                  buttonLabel={requestTypeConfig?.action_labels?.[actionName]}
                  iconName={iconConfig[actionName]}
                  requireConfirmation={requireConfirmation(
                    actionName,
                    requestTypeConfig?.request_type_properties,
                  )}
                  className={`requests request-action-button ${actionName} ${
                    requestTypeConfig?.request_type_properties?.dangerous &&
                    "dangerous"
                  }`}
                />
              );
            })}
          </Dropdown.Menu>
        </Dropdown>
      </React.Fragment>
    </Overridable>
  );
};

RequestActions.propTypes = {
  request: PropTypes.object.isRequired,
  size: PropTypes.string.isRequired,
};

export default Overridable.component(
  "InvenioRequests.RequestActions",
  RequestActions,
);
