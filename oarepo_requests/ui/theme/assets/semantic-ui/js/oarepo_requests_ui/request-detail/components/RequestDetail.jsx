import React, { useState, useEffect } from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { scrollTop } from "@js/oarepo_ui";
import {
  Button,
  Grid,
  List,
  Header,
  TransitionablePortal,
  Icon,
  Menu,
} from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";

import { ActionButtons, Timeline, TopicPreview, SideRequestInfo } from ".";

export const RequestDetail = ({ request }) => {
  const [activeTab, setActiveTab] = useState("timeline");
  const [scrollToTopVisible, setScrollToTopVisible] = useState(false);

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
    <>
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
            <ActionButtons request={request} />
          </Grid.Column>
        </Grid.Row>
        <Grid.Row>
          <Grid.Column>
            <Header as="h1">{requestHeader}</Header>
            {description && <Grid.Row as="p">{description}</Grid.Row>}
            {/* {renderReadOnlyData ?
              <List relaxed>
                {Object.keys(request.payload).map(key => (
                  <List.Item key={key}>
                    <List.Content>
                      <List.Header>{key}</List.Header>
                      <ReadOnlyCustomFields
                        className="requests-form-cf"
                        config={payloadUI}
                        data={{ [key]: request.payload[key] }}
                        templateLoaders={[
                          (widget) => import(`@js/oarepo_requests/components/common/${widget}.jsx`),
                          (widget) => import(`react-invenio-forms`)
                        ]}
                      />
                    </List.Content>
                  </List.Item>
                ))}
              </List> : null
            } */}
            <SideRequestInfo request={request} />
          </Grid.Column>
        </Grid.Row>
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
      </Grid>
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
          <div>
            <Icon size="large" name="chevron up" />
          </div>
          <div className="scroll-top-text">
            {i18next.t("to top").toUpperCase()}
          </div>
        </Button>
      </TransitionablePortal>
    </>
  );
};
