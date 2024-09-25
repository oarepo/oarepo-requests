import React, { useCallback } from "react";
import PropTypes from "prop-types";
import { SegmentGroup } from "semantic-ui-react";
import { CreateRequestButtonGroup, RequestListContainer } from ".";
import { RequestContextProvider } from "../contexts";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { http } from "@js/oarepo_ui";

export const RecordRequests = ({
  record: initialRecord,
  ContainerComponent,
  onBeforeAction,
  onAfterAction,
  onActionError,
}) => {
  const queryClient = useQueryClient();

  const {
    data: requestTypes,
    error: applicableRequestsLoadingError,
    isLoading: applicableRequestTypesLoading,
  } = useQuery(
    ["applicableRequestTypes", initialRecord.links["applicable-requests"]],
    () => http.get(initialRecord.links["applicable-requests"]),
    {
      enabled: !!initialRecord.links?.["applicable-requests"],
    }
  );
  console.log(applicableRequestTypesLoading);
  const {
    data: recordRequests,
    error: requestsLoadingError,
    isLoading: requestsLoading,
  } = useQuery(
    ["requests", initialRecord.links?.requests],
    () => http.get(initialRecord.links?.requests),
    {
      enabled: !!initialRecord.links?.requests,
    }
  );
  const applicableRequestTypes = requestTypes?.data?.hits?.hits;
  const requests = recordRequests?.data?.hits?.hits;
  const fetchNewRequests = useCallback(() => {
    queryClient.invalidateQueries(["applicableRequestTypes"]);
    queryClient.invalidateQueries(["requests"]);
  }, [queryClient]);
  return (
    <RequestContextProvider
      requests={{
        requests,
        requestTypes: applicableRequestTypes,
        // TODO: check this
        setRequests: () => {},
        fetchNewRequests,
        record: initialRecord,
        onBeforeAction,
        onAfterAction,
        onActionError,
      }}
    >
      <ContainerComponent>
        {applicableRequestTypes?.length > 0 && (
          <CreateRequestButtonGroup
            recordLoading={applicableRequestTypesLoading}
            recordLoadingError={applicableRequestsLoadingError}
          />
        )}
        {requests?.length > 0 && (
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
  onBeforeAction: PropTypes.func,
  onAfterAction: PropTypes.func,
  onActionError: PropTypes.func,
};

RecordRequests.defaultProps = {
  ContainerComponent: ({ children }) => (
    <SegmentGroup className="requests-container borderless">
      {children}
    </SegmentGroup>
  ),
  onBeforeAction: undefined,
  onAfterAction: undefined,
  onActionError: undefined,
};
