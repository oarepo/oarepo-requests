import React, { useState } from "react";
import PropTypes from "prop-types";

import Overridable, {
  OverridableContext,
  overrideStore,
} from "react-overridable";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import _sortBy from "lodash/sortBy";

import { List, Segment, Header, Button } from "semantic-ui-react";

import { CreateRequestButtonGroup, RequestListContainer } from ".";
import { RequestContextProvider, RecordContextProvider } from "../contexts";

/**
 * @typedef {import("../types").Request} Request
 * @typedef {import("../types").RequestType} RequestType
 */

export const RecordRequests = ({ record }) => {
  /** @type {RequestType[]} */
  const requestTypes = record.request_types ?? [];

  const requestsState = useState(_sortBy(record.requests, ["status_code"]) ?? []);

  return (
    <>
      {/* <OverridableContext.Provider value={overrideStore.getAll()}> */}
      <RecordContextProvider record={record}>
        <RequestContextProvider requests={requestsState}>
          {requestTypes && (
            <CreateRequestButtonGroup requestTypes={requestTypes} />
          )}
          {record?.requests && (
            <RequestListContainer requestTypes={requestTypes} />
          )}
        </RequestContextProvider>
      </RecordContextProvider>
      {/* </OverridableContext.Provider> */}
    </>
  );
}

RecordRequests.propTypes = {
  record: PropTypes.object.isRequired,
};