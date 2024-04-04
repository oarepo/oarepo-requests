import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";

import axios from "axios";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Loader, Dimmer } from "semantic-ui-react";
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

  const [isLoading, setIsLoading] = useState(true);

  const [requests, setRequests] = useState(sortByStatusCode(record?.requests ?? []) ?? []);
  const requestsSetter = React.useCallback(newRequests => setRequests(newRequests), [])

  useEffect(() => {
    setIsLoading(true);
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
      })
      .finally(() => {
        setIsLoading(false);
      });
    return () => setIsLoading(false);
  }, []);

  return (
    <RecordContextProvider record={record}>
      <RequestContextProvider requests={{ requests, setRequests: requestsSetter }}>
        {!_isEmpty(requestTypes) && (
          <CreateRequestButtonGroup requestTypes={requestTypes} />
        )}
        <RequestListContainer requestTypes={requestTypes} isLoading={isLoading} />
      </RequestContextProvider>
    </RecordContextProvider>
  );
}

RecordRequests.propTypes = {
  record: PropTypes.object.isRequired,
};