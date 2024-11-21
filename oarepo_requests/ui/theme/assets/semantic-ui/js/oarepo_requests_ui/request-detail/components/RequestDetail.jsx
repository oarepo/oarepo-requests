import React, { useState, useEffect, useMemo } from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { scrollTop } from "@js/oarepo_ui";
import {
  Button,
  Grid,
  Header,
  TransitionablePortal,
  Icon,
  Menu,
  Confirm,
  Loader,
  Message,
} from "semantic-ui-react";
import PropTypes from "prop-types";
import { useQuery, useIsMutating } from "@tanstack/react-query";
import { http } from "react-invenio-forms";
import {
  mapLinksToActions,
  ConfirmModalContextProvider,
  RequestCustomFields,
  SideRequestInfo,
  Timeline,
  CallbackContextProvider,
  TopicPreview,
} from "@js/oarepo_requests_common";
import { Formik } from "formik";
import _isEmpty from "lodash/isEmpty";

export const RequestDetail = ({
  request,
  timelinePageSize,
  onBeforeAction,
  onAfterAction,
  onActionError,
}) => {
  const [activeTab, setActiveTab] = useState("timeline");
  const [scrollToTopVisible, setScrollToTopVisible] = useState(false);
  const { data, isLoading } = useQuery(
    ["applicableCustomFields", request?.type],
    () => http.get(`/requests/configs/${request?.type}`),
    {
      enabled: !!request?.type,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    }
  );
  const customFields = data?.data?.custom_fields;
  const requestTypeProperties = data?.data?.request_type_properties;
  const actions = mapLinksToActions(
    request,
    customFields,
    requestTypeProperties
  );
  const isMutating = useIsMutating();
  useEffect(() => {
    const handleScrollButtonVisibility = () => {
      window.scrollY > 300
        ? setScrollToTopVisible(true)
        : setScrollToTopVisible(false);
    };
    window.addEventListener("scroll", handleScrollButtonVisibility);
    return () => {
      window.removeEventListener("scroll", handleScrollButtonVisibility);
    };
  }, []);

  const formikInitialValues = useMemo(() => {
    return {
      payload: !_isEmpty(request?.payload) ? request.payload : {},
    };
  }, [request?.payload]);

  const requestHeader = request?.stateful_name || request?.name;
  const description = request?.stateful_description || request?.description;
  return (
    <CallbackContextProvider
      value={{ onBeforeAction, onAfterAction, onActionError }}
    >
      <Formik initialValues={formikInitialValues}>
        {({ errors }) => (
          <ConfirmModalContextProvider requestOrRequestType={request}>
            {({ confirmDialogProps }) => (
              <Grid relaxed>
                <Grid.Row columns={2}>
                  <Grid.Column>
                    <Button
                      as="a"
                      compact
                      href="/me/requests/"
                      icon
                      labelPosition="left"
                    >
                      <Icon name="arrow left" />
                      {i18next.t("Back to requests")}
                    </Button>
                  </Grid.Column>
                  <Grid.Column floated="right" textAlign="right">
                    {actions.map(({ name, component: ActionComponent }) => (
                      <React.Fragment key={name}>
                        <ActionComponent
                          request={request}
                          extraData={requestTypeProperties}
                          isMutating={isMutating}
                        />
                      </React.Fragment>
                    ))}
                  </Grid.Column>
                </Grid.Row>
                <Confirm
                  {...confirmDialogProps}
                  className="requests dangerous-action-confirmation-modal"
                />
                {errors?.api && (
                  <Grid.Row>
                    <Grid.Column>
                      <Message negative>
                        <Message.Header>{errors.api}</Message.Header>
                      </Message>
                    </Grid.Column>
                  </Grid.Row>
                )}
                <Grid.Row>
                  <Grid.Column>
                    <Header as="h1">{requestHeader}</Header>
                    {description && <p>{description}</p>}
                    <SideRequestInfo request={request} />
                  </Grid.Column>
                </Grid.Row>
                <React.Fragment>
                  <RequestCustomFields
                    request={request}
                    customFields={customFields}
                    actions={actions}
                  />
                  <Loader active={isLoading} />
                </React.Fragment>
                <Grid.Row>
                  <Grid.Column>
                    <Menu tabular attached>
                      <Menu.Item
                        name="timeline"
                        content={i18next.t("Timeline")}
                        active={activeTab === "timeline"}
                        onClick={() => setActiveTab("timeline")}
                      />
                      {request?.topic?.links?.self_html && (
                        <Menu.Item
                          name="topic"
                          content={i18next.t("Record preview")}
                          active={activeTab === "topic"}
                          onClick={() => setActiveTab("topic")}
                        />
                      )}
                    </Menu>
                  </Grid.Column>
                </Grid.Row>
                <Grid.Row>
                  <Grid.Column>
                    {activeTab === "timeline" && (
                      <Timeline
                        request={request}
                        timelinePageSize={timelinePageSize}
                      />
                    )}
                    {activeTab === "topic" && (
                      <TopicPreview request={request} />
                    )}
                  </Grid.Column>
                </Grid.Row>
                <TransitionablePortal
                  open={scrollToTopVisible}
                  transition={{ animation: "fade up", duration: 300 }}
                >
                  <Button
                    onClick={scrollTop}
                    id="scroll-top-button"
                    secondary
                    circular
                    basic
                  >
                    <Icon size="large" name="chevron up" />
                    <div className="scroll-top-text">
                      {i18next.t("to top").toUpperCase()}
                    </div>
                  </Button>
                </TransitionablePortal>
              </Grid>
            )}
          </ConfirmModalContextProvider>
        )}
      </Formik>
    </CallbackContextProvider>
  );
};

RequestDetail.propTypes = {
  request: PropTypes.object,
  onBeforeAction: PropTypes.func,
  onAfterAction: PropTypes.func,
  onActionError: PropTypes.func,
  timelinePageSize: PropTypes.number,
};

RequestDetail.defaultProps = {
  onBeforeAction: undefined,
  onAfterAction: undefined,
  onActionError: undefined,
  timelinePageSize: 25,
};
