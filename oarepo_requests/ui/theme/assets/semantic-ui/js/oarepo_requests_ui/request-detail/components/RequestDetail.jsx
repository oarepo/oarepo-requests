import React from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Grid, List, Form, Divider, Comment, Header, Container, Icon } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import _sortBy from "lodash/sortBy";

import { ReadOnlyCustomFields } from "@js/oarepo_requests/components";
import { SideRequestInfo } from ".";

export const RequestDetail = ({ request }) => {
  const requestModalHeader = !_isEmpty(request?.title) ? request.title : (!_isEmpty(request?.name) ? request.name : request.type);
  const renderReadOnlyData = !_isEmpty(request?.payload);

  return (
    <Grid relaxed>
      <Grid.Row columns={2}>
        <Grid.Column>
          <Header as="h1">{requestModalHeader}</Header>
          {request?.description &&
            <Grid.Row as="p">
              {request.description}
            </Grid.Row>
          }
        </Grid.Column>
        <Grid.Column floated="right" textAlign="right">
          <Button positive compact icon="check" content={i18next.t("Accept")} />
          <Button compact icon="close" content={i18next.t("Cancel")} />
          <Button negative compact icon="close" content={i18next.t("Decline")} />
        </Grid.Column>
      </Grid.Row>
      <Grid.Row columns={2}>
        <Grid.Column as="aside" width={3} only="mobile" className="sidebar">
          <SideRequestInfo request={request} />
        </Grid.Column>
        <Grid.Column as="article" width={13}>
          {renderReadOnlyData &&
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
                        (widget) => import(`../components/common/${widget}.jsx`),
                        (widget) => import(`react-invenio-forms`)
                      ]}
                    />
                  </List.Content>
                </List.Item>
              ))}
            </List>
          }
          {/* If events are enabled for this request type, you can see the timeline of events and create new events. */}
          {/* {!_isEmpty(eventTypes) &&
                    <>
                      <Divider horizontal>{i18next.t("Timeline")}</Divider>
                      {!_isEmpty(events) &&
                        <Comment.Group>
                          {events.map(event => {
                            const eventPayloadUI = eventTypes.filter(eventType => eventType.id === event.type_code)[0]?.payload_ui;
                            return (
                              <Comment key={event.id}>
                                <Comment.Content>
                                  <Comment.Author as="a" href={event.created_by?.link}>{event.created_by.label}</Comment.Author>
                                  <Comment.Metadata>
                                    <div>{event?.created}</div>
                                  </Comment.Metadata>
                                  <Comment.Text>
                                    <ReadOnlyCustomFields
                                      className="requests-events-read-only-cf"
                                      config={eventPayloadUI}
                                      data={event.payload}
                                      templateLoaders={[
                                        (widget) => import(`./${widget}.jsx`),
                                        (widget) => import(`react-invenio-forms`)
                                      ]}
                                    // fieldPathPrefix="payload"
                                    />
                                  </Comment.Text>
                                </Comment.Content>
                              </Comment>
                            )
                          })}
                        </Comment.Group>
                      }
                      {eventTypes.map(event => (
                        <RequestModal key={event.id} request={event} requestModalType={REQUEST_TYPE.CREATE} isEventModal
                          triggerButton={<Button key={event.id} compact primary icon="plus" labelPosition="left" content={event.name} />} />
                      ))}
                    </>
                  } */}
        </Grid.Column>
        <Grid.Column as="aside" width={3} only="tablet computer" className="sidebar">
          <SideRequestInfo request={request} />
        </Grid.Column>
      </Grid.Row>
    </Grid>
  );
}
