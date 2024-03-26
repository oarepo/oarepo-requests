import React, { useState } from "react";
import PropTypes from "prop-types";

import _sortBy from "lodash/sortBy";

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
  );
}

RecordRequests.propTypes = {
  record: PropTypes.object.isRequired,
};