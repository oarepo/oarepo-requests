import React, { useEffect, useState, useCallback } from "react";
import PropTypes from "prop-types";

import axios from "axios";
import { SegmentGroup } from "semantic-ui-react";

import { CreateRequestButtonGroup, RequestListContainer } from ".";
import { RequestContextProvider } from "../contexts";
import { sortByStatusCode } from "../utils";

export const RecordRequests = ({
  record: initialRecord,
  ContainerComponent,
  onErrorCallback,
  saveDraft,
  shouldRedirectToEdit = true,
}) => {
  const [recordLoading, setRecordLoading] = useState(true);
  const [requestsLoading, setRequestsLoading] = useState(true);

  const [recordLoadingError, setRecordLoadingError] = useState(null);
  const [requestsLoadingError, setRequestsLoadingError] = useState(null);

  const [record, setRecord] = useState(initialRecord);
  const [requests, setRequests] = useState(
    sortByStatusCode(record?.requests ?? []) ?? []
  );

  const requestsSetter = useCallback(
    (newRequests) => setRequests(newRequests),
    []
  );

  const fetchRecord = useCallback(
    async (initRequests = false) => {
      setRecordLoading(true);
      setRecordLoadingError(null);
      return axios({
        method: "get",
        url: record.links?.self + "?expand=true",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/vnd.inveniordm.v1+json",
        },
      })
        .then((response) => {
          setRecord(response.data);
          initRequests &&
            setRequests(
              sortByStatusCode(response.data?.expanded?.requests ?? [])
            );
        })
        .catch((error) => {
          setRecordLoadingError(error);
          initRequests && setRequestsLoadingError(error);
        })
        .finally(() => {
          setRecordLoading(false);
          initRequests && setRequestsLoading(false);
        });
    },
    [record.links?.self]
  );

  const fetchRequests = useCallback(async () => {
    setRequestsLoading(true);
    setRequestsLoadingError(null);
    return axios({
      method: "get",
      url: record.links?.requests,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/vnd.inveniordm.v1+json",
      },
    })
      .then((response) => {
        setRequests(sortByStatusCode(response.data?.hits?.hits));
      })
      .catch((error) => {
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
    fetchRecord(true);
  }, [fetchRecord]);

  const requestTypes = record?.expanded?.request_types ?? [];
  return (
    <RequestContextProvider
      requests={{
        requests,
        requestTypes,
        setRequests: requestsSetter,
        fetchNewRequests,
        onErrorCallback,
        record: record,
        saveDraft,
        shouldRedirectToEdit,
      }}
    >
      <ContainerComponent>
        <CreateRequestButtonGroup
          recordLoading={recordLoading}
          recordLoadingError={recordLoadingError}
        />
        <RequestListContainer
          requestsLoading={requestsLoading}
          requestsLoadingError={requestsLoadingError}
        />
      </ContainerComponent>
    </RequestContextProvider>
  );
};

RecordRequests.propTypes = {
  record: PropTypes.object.isRequired,
  ContainerComponent: PropTypes.func,
  onErrorCallback: PropTypes.func,
};

RecordRequests.defaultProps = {
  ContainerComponent: ({ children }) => (
    <SegmentGroup className="requests-container borderless">
      {children}
    </SegmentGroup>
  ),
  onErrorCallback: undefined,
};
