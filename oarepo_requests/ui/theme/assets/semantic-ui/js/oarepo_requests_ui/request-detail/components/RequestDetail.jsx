import React, { useState, useEffect } from "react";

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
} from "semantic-ui-react";
import { TopicPreview } from ".";
import PropTypes from "prop-types";
import { useQuery } from "@tanstack/react-query";
import { http } from "react-invenio-forms";
import {
  mapLinksToActions,
  ConfirmModalContextProvider,
  RequestCustomFields,
  SideRequestInfo,
  Timeline,
} from "@js/oarepo_requests_common";
import { Formik } from "formik";

export const RequestDetail = ({ request }) => {
  const [activeTab, setActiveTab] = useState("timeline");
  const [scrollToTopVisible, setScrollToTopVisible] = useState(false);
  const {
    data,
    error: customFieldsLoadingError,
    isLoading,
  } = useQuery(
    ["applicableCustomFields", request?.type],
    () => http.get(`/requests/configs/${request?.type}`),
    {
      enabled: !!request?.type,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    }
  );

  const customFields = data?.data?.custom_fields;
  const extra_data = data?.data?.extra_data;
  const actions = mapLinksToActions(request, customFields, extra_data);

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

  // const renderReadOnlyData = !_isEmpty(request?.payload);
  const requestHeader = request?.stateful_name || request?.name;
  const description = request?.stateful_description || request?.description;
  return (
    <Formik initialValues={{}}>
      <ConfirmModalContextProvider>
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
                {/* Action Buttons */}
                {actions.map(({ name, component: ActionComponent }) => (
                  <React.Fragment key={name}>
                    <ActionComponent request={request} extraData={extra_data} />
                  </React.Fragment>
                ))}
              </Grid.Column>
            </Grid.Row>
            <Confirm {...confirmDialogProps} />

            <Grid.Row>
              <Grid.Column>
                <Header as="h1">{requestHeader}</Header>
                {description && <p>{description}</p>}
                <SideRequestInfo request={request} />
              </Grid.Column>
            </Grid.Row>
            <RequestCustomFields
              request={request}
              customFields={customFields}
              actions={actions}
            />
            <Grid.Row>
              <Grid.Column>
                <Menu tabular attached>
                  <Menu.Item
                    name="timeline"
                    content={i18next.t("Timeline")}
                    active={activeTab === "timeline"}
                    onClick={() => setActiveTab("timeline")}
                  />
                  <Menu.Item
                    name="topic"
                    content={`${i18next.t("Record")} ${i18next.t("preview")}`}
                    active={activeTab === "topic"}
                    onClick={() => setActiveTab("topic")}
                  />
                </Menu>
              </Grid.Column>
            </Grid.Row>

            <Grid.Row>
              <Grid.Column>
                {activeTab === "timeline" && <Timeline request={request} />}
                {activeTab === "topic" && <TopicPreview request={request} />}
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
    </Formik>
  );
};

RequestDetail.propTypes = {
  request: PropTypes.object,
};
