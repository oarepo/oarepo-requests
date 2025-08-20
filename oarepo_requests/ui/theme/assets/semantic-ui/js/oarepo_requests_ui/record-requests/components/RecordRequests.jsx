import React, { useCallback, useEffect, useState } from "react";
import PropTypes from "prop-types";
import { CreateRequestButtonGroup, RequestListContainer } from ".";
import {
  RequestContextProvider,
  CallbackContextProvider,
} from "@js/oarepo_requests_common";
import {
  useQuery,
  useQueryClient,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import _isEmpty from "lodash/isEmpty";
import { httpVnd } from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { OverridableContext, overrideStore } from "react-overridable";
import overrides from "@js/oarepo_requests_common/overrides";
import { Accordion } from "semantic-ui-react";

const overriddenComponents = {
  ...overrides,
  ...overrideStore.getAll(),
};

export const requestButtonsDefaultIconConfig = {
  delete_published_record: { icon: "trash" },
  publish_draft: { icon: "upload" },
  publish_new_version: { icon: "upload" },
  publish_changed_metadata: { icon: "upload" },
  new_version: { icon: "tag" },
  edit_published_record: { icon: "pencil" },
  assign_doi: { icon: "address card" },
  delete_doi: { icon: "remove" },
  created: { icon: "paper plane" },
  initiate_community_migration: { icon: "exchange" },
  confirm_community_migration: { icon: "exchange" },
  secondary_community_submission: { icon: "users" },
  remove_secondary_community: { icon: "remove" },
  submitted: { icon: "clock" },
  default: { icon: "plus" },
};

const queryClient = new QueryClient();

const DefaultContainerComponent = ({ children }) => (
  <div className="requests-container borderless">{children}</div>
);

DefaultContainerComponent.propTypes = {
  // eslint-disable-next-line react/require-default-props
  children: PropTypes.node,
};

const RecordRequests = ({
  record: initialRecord,
  ContainerComponent = DefaultContainerComponent,
  onBeforeAction,
  onAfterAction,
  onErrorPlugins = [],
  requestButtonsIconsConfig,
  actionExtraContext,
}) => {
  const queryClient = useQueryClient();
  const [actionsLocked, setActionsLocked] = useState(false);
  const {
    data: requestTypes,
    error: applicableRequestsLoadingError,
    isFetching: applicableRequestTypesLoading,
  } = useQuery(
    ["applicableRequestTypes"],
    () => httpVnd.get(initialRecord.links["applicable-requests"]),
    {
      enabled: !!initialRecord.links?.["applicable-requests"],
      refetchOnWindowFocus: false,
    }
  );
  const {
    data: recordRequests,
    error: requestsLoadingError,
    isFetching: requestsLoading,
  } = useQuery(["requests"], () => httpVnd.get(initialRecord.links?.requests), {
    enabled: !!initialRecord.links?.requests,
    refetchOnWindowFocus: false,
  });
  const applicableRequestTypes = requestTypes?.data?.hits?.hits;
  const createRequests = applicableRequestTypes?.filter(
    (requestType) => requestType.links.actions?.create
  );

  const requests = recordRequests?.data?.hits?.hits;
  const fetchNewRequests = useCallback(() => {
    queryClient.invalidateQueries(["applicableRequestTypes"]);
    queryClient.invalidateQueries(["requests"]);
  }, [queryClient]);
  const openRequests = requests?.filter(
    (request) =>
      request.is_open || request?.status_code.toLowerCase() === "created"
  );

  useEffect(() => {
    const handleBeforeUnload = () => {
      setActionsLocked(false);
    };

    window.addEventListener("unload", handleBeforeUnload);

    return () => {
      window.removeEventListener("unload", handleBeforeUnload);
    };
  }, [setActionsLocked]);

  return (
    <RequestContextProvider
      value={{
        requests,
        requestTypes: applicableRequestTypes,
        record: initialRecord,
        requestButtonsIconsConfig: {
          ...requestButtonsDefaultIconConfig,
          ...requestButtonsIconsConfig,
        },
      }}
    >
      <CallbackContextProvider
        value={{
          onBeforeAction,
          onAfterAction,
          onErrorPlugins,
          fetchNewRequests,
          actionExtraContext,
          actionsLocked,
          setActionsLocked,
        }}
      >
        {initialRecord?.id && (
          <ContainerComponent>
            <Accordion
              fluid
              exclusive={false}
              defaultActiveIndex={[0, 1]}
              panels={[
                ...(!_isEmpty(createRequests) || applicableRequestTypesLoading || applicableRequestsLoadingError)
                  ? [
                      {
                        key: "new-request",
                        title: i18next.t("New Request"),
                        content: {
                          content: (
                            <CreateRequestButtonGroup
                              applicableRequestsLoading={applicableRequestTypesLoading}
                              applicableRequestsLoadingError={
                                applicableRequestsLoadingError
                              }
                              createRequests={createRequests}
                            />
                          ),
                        },
                      },
                    ]
                  : [],
                ...(!_isEmpty(openRequests) || requestsLoading || requestsLoadingError)
                  ? [
                      {
                        key: "open-requests",
                        title: i18next.t("Open Requests"),
                        content: {
                          content: (
                            <RequestListContainer
                              requestsLoading={requestsLoading}
                              requestsLoadingError={requestsLoadingError}
                              openRequests={openRequests}
                            />
                          ),
                        },
                      },
                    ]
                  : [],
              ]}
            />
          </ContainerComponent>
        )}
      </CallbackContextProvider>
    </RequestContextProvider>
  );
};

/* eslint-disable react/require-default-props */
RecordRequests.propTypes = {
  record: PropTypes.object.isRequired,
  ContainerComponent: PropTypes.func,
  onBeforeAction: PropTypes.func,
  onAfterAction: PropTypes.func,
  onErrorPlugins: PropTypes.array,
  requestButtonsIconsConfig: PropTypes.object,
  actionExtraContext: PropTypes.object,
};
/* eslint-enable react/require-default-props */

const RecordRequestsWithQueryClient = ({
  record: initialRecord,
  ContainerComponent = DefaultContainerComponent,
  onBeforeAction,
  onAfterAction,
  onErrorPlugins = [],
  requestButtonsIconsConfig,
  actionExtraContext,
}) => {
  return (
    <OverridableContext.Provider value={overriddenComponents}>
      <QueryClientProvider client={queryClient}>
        <RecordRequests
          record={initialRecord}
          ContainerComponent={ContainerComponent}
          onBeforeAction={onBeforeAction}
          onAfterAction={onAfterAction}
          onErrorPlugins={onErrorPlugins}
          requestButtonsIconsConfig={requestButtonsIconsConfig}
          actionExtraContext={actionExtraContext}
        />
      </QueryClientProvider>
    </OverridableContext.Provider>
  );
};

/* eslint-disable react/require-default-props */
RecordRequestsWithQueryClient.propTypes = {
  record: PropTypes.object.isRequired,
  ContainerComponent: PropTypes.func,
  onBeforeAction: PropTypes.func,
  onAfterAction: PropTypes.func,
  onErrorPlugins: PropTypes.array,
  requestButtonsIconsConfig: PropTypes.object,
  actionExtraContext: PropTypes.object,
};
/* eslint-enable react/require-default-props */

export { RecordRequestsWithQueryClient as RecordRequests };
