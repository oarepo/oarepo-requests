// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
// Copyright (C) 2024 KTH Royal Institute of Technology.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import RequestMetadata from "@js/invenio_requests/request/RequestMetadata";
import React, { Component } from "react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import { Grid, Container, Header } from "semantic-ui-react";
import { Timeline } from "@js/invenio_requests/timeline";
import { RequestCustomFields } from "./components";

export class RequestDetails extends Component {
  render() {
    const { request, userAvatar, permissions, config } = this.props;
    return (
      <React.Fragment>
        <Container>
          <Header as="h2" dividing>
            {request?.stateful_name || request?.name || request?.type}
          </Header>
          <p>{request?.stateful_description || request?.description}</p>
          <RequestCustomFields request={request} />
        </Container>
        <Grid stackable reversed="mobile">
          <Grid.Column mobile={16} tablet={12} computer={13}>
            <Timeline
              userAvatar={userAvatar}
              request={request}
              permissions={permissions}
            />
          </Grid.Column>
          <Grid.Column mobile={16} tablet={4} computer={3}>
            <RequestMetadata
              request={request}
              permissions={permissions}
              config={config}
            />
          </Grid.Column>
        </Grid>
      </React.Fragment>
    );
  }
}

RequestDetails.propTypes = {
  request: PropTypes.object.isRequired,
  userAvatar: PropTypes.string,
  permissions: PropTypes.object.isRequired,
  config: PropTypes.object.isRequired,
};

RequestDetails.defaultProps = {
  userAvatar: "",
};
