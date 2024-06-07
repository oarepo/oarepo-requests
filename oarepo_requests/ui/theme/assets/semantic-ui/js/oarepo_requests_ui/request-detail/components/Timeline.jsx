import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Grid, List, Form, Divider, Comment, Header, Container, Icon, Menu, Message, Feed, Dimmer, Loader, Placeholder, Segment } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import _sortBy from "lodash/sortBy";
import _has from "lodash/has";
import axios from "axios";
import { delay } from "bluebird";

import { ReadOnlyCustomFields } from "@js/oarepo_requests/components";
import { EventSubmitForm } from ".";
import { hasAll, hasAny, sanitizeInput } from "../utils";

export const Timeline = ({ request }) => {
  const [events, setEvents] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchEvents = async () => {
    setIsLoading(true);
    setError(null);
    try {
      await delay(2000); // TODO: The backend is super slow to resolve the Timeline. Added super slow delay.
      const response = await axios.get(request.links?.timeline, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        }
      });
      setEvents(response.data.hits.hits);
    } catch (error) {
      setError(error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
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
                {Array.from({ length: events.length < 5 ? 5 : events.length }).map((_, index) => (
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
                  const isRenderable = hasAll(event, 'created', 'payload') && hasAny(event.payload, 'event', 'content');
                  const eventLabel = isRenderable ? event.payload?.event ?? i18next.t("commented") : null;
                  return isRenderable ? (
                  <Feed.Event key={event.id}>
                    <Feed.Label>
                      <Icon name='user circle' />
                    </Feed.Label>
                    <Feed.Content>
                      <Feed.Summary>
                        {_has(event, "created_by.user") ? 
                          <><Feed.User>{event.created_by.user}</Feed.User> {eventLabel} this request on<Feed.Date>{event.created}</Feed.Date></> : 
                          <span>Request {eventLabel} on {event.created}</span>
                        } 
                      </Feed.Summary>
                      {_has(event.payload, "content") && 
                        <Feed.Extra text>
                          <div dangerouslySetInnerHTML={{ __html: sanitizeInput(event.payload.content) }} />
                        </Feed.Extra>
                      }
                    </Feed.Content>
                  </Feed.Event>
                  ) : null;
                })}
              </Feed> :
              null
        }
      </Dimmer.Dimmable>
      <EventSubmitForm request={request} fetchEvents={fetchEvents} />
    </>
  );
}
