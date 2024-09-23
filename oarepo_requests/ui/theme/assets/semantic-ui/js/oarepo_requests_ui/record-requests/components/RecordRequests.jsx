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
  const [applicableRequestTypesLoading, setApplicableRequestTypesLoading] =
    useState(true);
  const [requestsLoading, setRequestsLoading] = useState(true);

  const [applicableRequestsLoadingError, setApplicableRequestsLoadingError] =
    useState(null);
  const [requestsLoadingError, setRequestsLoadingError] = useState(null);

  const [applicableRequestTypes, setApplicableRequestTypes] = useState([]);
  const [requests, setRequests] = useState([]);
  console.log(applicableRequestTypes);
  const requestsSetter = useCallback(
    (newRequests) => setRequests(newRequests),
    []
  );

  const fetchApplicableRequestTypes = useCallback(async () => {
    console.log(initialRecord.links["applicable-requests"]);

    setApplicableRequestTypesLoading(true);
    setApplicableRequestsLoadingError(null);
    return axios({
      method: "get",
      url: initialRecord.links["applicable-requests"],
      headers: {
        "Content-Type": "application/json",
        Accept: "application/vnd.inveniordm.v1+json",
      },
    })
      .then((response) => {
        setApplicableRequestTypes(response.data.hits.hits);
      })
      .catch((error) => {
        setApplicableRequestsLoadingError(error);
        setRequestsLoadingError(error);
      })
      .finally(() => {
        setApplicableRequestTypesLoading(false);
        setApplicableRequestTypesLoading(false);
      });
  }, [initialRecord.links?.self]);

  const fetchRequests = useCallback(async () => {
    setRequestsLoading(true);
    setRequestsLoadingError(null);
    return axios({
      method: "get",
      url: initialRecord.links?.requests,
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
  }, [initialRecord.links?.requests]);

  const fetchNewRequests = useCallback(() => {
    fetchApplicableRequestTypes();
    fetchRequests();
  }, [fetchApplicableRequestTypes, fetchRequests]);

  useEffect(() => {
    fetchApplicableRequestTypes();
    fetchRequests();
  }, [fetchApplicableRequestTypes, fetchRequests]);

  return (
    <RequestContextProvider
      requests={{
        requests,
        requestTypes: applicableRequestTypes,
        setRequests: requestsSetter,
        fetchNewRequests,
        onErrorCallback,
        record: initialRecord,
        saveDraft,
        shouldRedirectToEdit,
      }}
    >
      <ContainerComponent>
        {applicableRequestTypes.length > 0 && (
          <CreateRequestButtonGroup
            recordLoading={applicableRequestTypesLoading}
            recordLoadingError={applicableRequestsLoadingError}
          />
        )}
        {requests.length > 0 && (
          <RequestListContainer
            requestsLoading={requestsLoading}
            requestsLoadingError={requestsLoadingError}
          />
        )}
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
