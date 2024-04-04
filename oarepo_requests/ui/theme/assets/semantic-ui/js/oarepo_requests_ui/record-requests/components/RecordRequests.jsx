import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";

import axios from "axios";
import _isEmpty from "lodash/isEmpty";

import { CreateRequestButtonGroup, RequestListContainer } from ".";
import { RequestContextProvider, RecordContextProvider } from "../contexts";
import { sortByStatusCode } from "../utils";

export const RecordRequests = ({ record: initialRecord }) => {
  const [recordLoading, setRecordLoading] = useState(true);
  const [requestsLoading, setRequestsLoading] = useState(true);

  const [record, setRecord] = useState(initialRecord);
  const [requests, setRequests] = useState(sortByStatusCode(record?.requests ?? []) ?? []);
  const requestsSetter = React.useCallback(newRequests => setRequests(newRequests), [])

  useEffect(() => {
    setRecordLoading(true);
    axios({
      method: 'get',
      url: record.links?.self,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.inveniordm.v1+json'
      }
    })
      .then(response => {
        setRecord(response.data);
      })
      .catch(error => {
        console.log(error);
      })
      .finally(() => {
        setRecordLoading(false);
      });
    return () => setRecordLoading(false);
  }, []);

  useEffect(() => {
    setRequestsLoading(true);
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
        setRequestsLoading(false);
      });
    return () => setRequestsLoading(false);
  }, []);

  return (
    <RecordContextProvider record={record}>
      <RequestContextProvider requests={{ requests, setRequests: requestsSetter }}>
        <CreateRequestButtonGroup requestTypes={record?.request_types ?? []} isLoading={recordLoading} />
        <RequestListContainer requestTypes={record?.request_types ?? []} isLoading={requestsLoading} />
      </RequestContextProvider>
    </RecordContextProvider>
  );
}

RecordRequests.propTypes = {
  record: PropTypes.object.isRequired,
};