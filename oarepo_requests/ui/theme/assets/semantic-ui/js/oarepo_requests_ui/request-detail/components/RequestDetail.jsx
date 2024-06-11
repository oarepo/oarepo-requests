import React, { useState } from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Grid, List, Form, Divider, Comment, Header, Container, Icon, Menu } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import _sortBy from "lodash/sortBy";

import { ActionButtons, MainRequestDetails, TopicPreview } from ".";

export const RequestDetail = ({ request }) => {
  const [activeTab, setActiveTab] = useState("details");

  const requestModalHeader = !_isEmpty(request?.title) ? request.title : (!_isEmpty(request?.name) ? request.name : request.type);

  return (
    <Grid relaxed>
      <Grid.Row columns={2}>
        <Grid.Column>
          <Button as="a" compact href="/me/requests/" icon labelPosition="left">
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
          <Header as="h1">{requestModalHeader}</Header>
          {request?.description &&
            <Grid.Row as="p">
              {request.description}
            </Grid.Row>
          }
        </Grid.Column>
      </Grid.Row>
      <Grid.Row>
        <Grid.Column>
          <Menu tabular attached>
            <Menu.Item
              name='details'
              content={i18next.t("Details")}
              active={activeTab === 'details'}
              onClick={() => setActiveTab('details')}
            />
            <Menu.Item
              name='topic'
              content={`${i18next.t("Record")} ${i18next.t("preview")}`}
              active={activeTab === 'topic'}
              onClick={() => setActiveTab('topic')}
            />
          </Menu>
        </Grid.Column>
      </Grid.Row>
      {activeTab === 'details' && <MainRequestDetails request={request} />}
      {activeTab === 'topic' && <TopicPreview request={request} />}
    </Grid>
  );
}
