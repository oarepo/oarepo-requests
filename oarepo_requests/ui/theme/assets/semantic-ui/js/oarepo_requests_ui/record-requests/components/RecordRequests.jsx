import React, { useEffect, useState, useCallback } from "react";
import PropTypes from "prop-types";

import axios from "axios";

import { CreateRequestButtonGroup, RequestListContainer } from ".";
import { RequestContextProvider } from "../contexts";
import { sortByStatusCode } from "../utils";

export const RecordRequests = ({ record: initialRecord }) => {
  const [recordLoading, setRecordLoading] = useState(true);
  const [requestsLoading, setRequestsLoading] = useState(true);

  const [recordLoadingError, setRecordLoadingError] = useState(null);
  const [requestsLoadingError, setRequestsLoadingError] = useState(null);

  const [record, setRecord] = useState(initialRecord);
  const [requests, setRequests] = useState(sortByStatusCode(record?.requests ?? []) ?? []);

  const requestsSetter = useCallback(newRequests => setRequests(newRequests), []);

  const fetchRecord = useCallback(async () => {
    setRecordLoading(true);
    setRecordLoadingError(null);
    return axios({
      method: 'get',
      url: record.links?.self + "?expand=true",
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.inveniordm.v1+json'
      }
    })
      .then(response => {
        setRecord(response.data);
        return response.data;
      })
      .catch(error => {
        setRecordLoadingError(error);
        throw error;
      })
      .finally(() => {
        setRecordLoading(false);
      });
  }, [record.links?.self]);

  const fetchRequests = useCallback(async () => {
    setRequestsLoading(true);
    setRequestsLoadingError(null);
    return axios({
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
        setRequestsLoadingError(error);
      })
      .finally(() => {
        setRequestsLoading(false);
      });
  }, [record.links?.requests]);

  const fetchNewRequests = useCallback(() => {
    fetchRecord();
    fetchRequests();
  }, [fetchRecord, fetchRequests]);

  useEffect(() => {
    fetchRecord()
      .then(record => {
        setRequests(sortByStatusCode(record?.expanded?.requests ?? []));
      })
      .catch(error => {
        setRequestsLoadingError(error);
      })
      .finally(() => {
        setRequestsLoading(false);
      });
  }, [fetchRecord]);

  return (
    <>
      <CreateRequestButtonGroup
        requestTypes={record?.expanded?.request_types ?? []}
        isLoading={recordLoading}
        loadingError={recordLoadingError}
        fetchNewRequests={fetchNewRequests}
      />
      <RequestContextProvider requests={{ requests, setRequests: requestsSetter }}>
        <RequestListContainer
          requestTypes={record?.expanded?.request_types ?? []}
          isLoading={requestsLoading}
          loadingError={requestsLoadingError}
          fetchNewRequests={fetchNewRequests}
        />
      </RequestContextProvider>
    </>
  );
}

RecordRequests.propTypes = {
  record: PropTypes.object.isRequired,
};