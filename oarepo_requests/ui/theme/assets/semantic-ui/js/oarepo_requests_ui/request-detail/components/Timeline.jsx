import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Grid, List, Form, Divider, Comment, Header, Container, Icon, Menu, Message, Feed, Dimmer, Loader, Placeholder, Segment } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import _sortBy from "lodash/sortBy";
import axios from "axios";

import { ReadOnlyCustomFields } from "@js/oarepo_requests/components";
import { SideRequestInfo } from ".";

export const Timeline = ({ request }) => {
  const [events, setEvents] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    setError(null);
    axios
      .get(`${request.links.timeline}`, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      })
      .then(response => {
        setEvents(response.data.hits.hits)
      })
      .catch(error => {
        console.error("Error while fetching timeline events", error);
        setError(error);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  return (
    <>
      <Divider horizontal>{i18next.t("Timeline")}</Divider>
      <Dimmer.Dimmable blurring dimmed={isLoading}>
        <Dimmer active={isLoading} inverted>
          <Loader indeterminate size="big">{i18next.t("Loading timeline...")}</Loader>
        </Dimmer>
        {error ?
          <Message negative>
            <Message.Header>{i18next.t("Error while fetching timeline events")}</Message.Header>
            <p>{error?.message}</p>
          </Message> :
          isLoading ?
            <Segment basic>
              <Placeholder fluid>
                {Array.from({ length: 5 }).map((_, index) => (
                  <Placeholder.Header image key={index}>
                    <Placeholder.Line />
                    <Placeholder.Line />
                  </Placeholder.Header>
                ))}
              </Placeholder> 
            </Segment> :
            !_isEmpty(events) ?
              <Feed>
                {events.map(event => {
                  const isRenderable = event?.payload?.event && event?.created;
                  return isRenderable ? (
                  <Feed.Event key={event.id}>
                    <Feed.Label>
                      <Icon name='user circle' />
                    </Feed.Label>
                    <Feed.Content>
                      <Feed.Summary>
                        {event?.created_by?.user ? 
                          <><Feed.User>{event.created_by.user}</Feed.User> {event.payload.event} this request on<Feed.Date>{event.created}</Feed.Date></> : 
                          <span>Request {event.payload.event} on {event.created}</span>
                        } 
                      </Feed.Summary>
                      {event?.payload?.content && <Feed.Extra text>{event.payload.content}</Feed.Extra>}
                    </Feed.Content>
                  </Feed.Event>
                  ) : null;
                })}
              </Feed> :
              null
        }
      </Dimmer.Dimmable>
    </>
  );
}
