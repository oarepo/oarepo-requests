import React, { useState, useEffect, useCallback, useRef } from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Message, Feed, Dimmer, Loader, Placeholder, Segment } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import axios from "axios";
import { delay } from "bluebird";

import { EventSubmitForm, TimelineEvent } from ".";

export const Timeline = ({ request }) => {
  const [events, setEvents] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const abortControllerRef = useRef(new AbortController());

  const fetchEvents = useCallback(async () => {
    const abortController = abortControllerRef.current;
    setIsLoading(true);
    setError(null);
    try {
      await delay(2000); // TODO: The backend is super slow to resolve the Timeline. Added super slow delay.
      const response = await axios.get(request.links?.timeline, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/vnd.inveniordm.v1+json'
        },
        signal: abortController.signal
      });
      if (!abortController.signal.aborted) {
        setEvents(response.data.hits.hits);
      }
    } catch (error) {
      setError(error);
    } finally {
      if (!abortController.signal.aborted) {
        setIsLoading(false);
      }
    }
  }, [request.links.timeline]);

  useEffect(() => {
    const abortController = abortControllerRef.current;
    fetchEvents();
    return () => {
      abortController.abort();
    }
  }, [fetchEvents]);

  return (
    <>
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
                {events.map(event => <TimelineEvent key={event.id} event={event} />)}
              </Feed> :
              null
        }
      </Dimmer.Dimmable>
      <EventSubmitForm request={request} fetchEvents={fetchEvents} />
    </>
  );
}
