import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";

import axios from "axios";
import _sortBy from "lodash/sortBy";
import _isEmpty from "lodash/isEmpty";

import { CreateRequestButtonGroup, RequestListContainer } from ".";
import { RequestContextProvider, RecordContextProvider } from "../contexts";

/**
 * @typedef {import("../types").Request} Request
 * @typedef {import("../types").RequestType} RequestType
 */

export const RecordRequests = ({ record }) => {
  /** @type {RequestType[]} */
  const requestTypes = record?.request_types ?? [];

  const requestsState = useState(_sortBy(record?.requests ?? [], ["status_code"]) ?? []);

  useEffect(() => {
    axios({
      method: 'get',
      url: record.links?.requests,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.inveniordm.v1+json'
      }
    })
      .then(response => {
        requestsState[1](_sortBy(response.data?.hits?.hits, ["status_code"]));
      })
      .catch(error => {
        console.log(error);
      });
  }, []);

  return (
    <RecordContextProvider record={record}>
      <RequestContextProvider requests={requestsState}>
        {!_isEmpty(requestTypes) && (
          <CreateRequestButtonGroup requestTypes={requestTypes} />
        )}
        {!_isEmpty(record?.requests) && (
          <RequestListContainer requestTypes={requestTypes} />
        )}
      </RequestContextProvider>
    </RecordContextProvider>
  );
}

RecordRequests.propTypes = {
  record: PropTypes.object.isRequired,
};