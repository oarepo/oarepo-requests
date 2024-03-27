import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";

import axios from "axios";
import _isEmpty from "lodash/isEmpty";

import { CreateRequestButtonGroup, RequestListContainer } from ".";
import { RequestContextProvider, RecordContextProvider } from "../contexts";
import { sortByStatusCode } from "../utils";

/**
 * @typedef {import("../types").Request} Request
 * @typedef {import("../types").RequestType} RequestType
 */

export const RecordRequests = ({ record }) => {
  /** @type {RequestType[]} */
  const requestTypes = record?.request_types ?? [];

  const [requests, setRequests] = useState(sortByStatusCode(record?.requests ?? []) ?? []);

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
        setRequests(sortByStatusCode(response.data?.hits?.hits));
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
        {!_isEmpty(requests) && (
          <RequestListContainer requestTypes={requestTypes} />
        )}
      </RequestContextProvider>
    </RecordContextProvider>
  );
}

RecordRequests.propTypes = {
  record: PropTypes.object.isRequired,
};