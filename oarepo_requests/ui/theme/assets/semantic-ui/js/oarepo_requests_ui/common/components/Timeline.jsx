import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import {
  Message,
  Feed,
  Dimmer,
  Loader,
  Placeholder,
  Segment,
} from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import {
  EventSubmitForm,
  TimelineEvent,
} from "../../request-detail/components";
import PropTypes from "prop-types";
import { http } from "@js/oarepo_ui";
import { useQuery } from "@tanstack/react-query";

export const Timeline = ({ request }) => {
  const {
    data: events,
    error,
    isFetching,
  } = useQuery(["requestEvents"], () => http.get(request.links?.timeline), {
    enabled: !!request.links?.timeline,
    refetchOnWindowFocus: false,
  });

  return (
    <>
      <Dimmer.Dimmable blurring dimmed={isFetching}>
        <Dimmer active={isFetching} inverted>
          <Loader indeterminate size="big">
            {i18next.t("Loading timeline...")}
          </Loader>
        </Dimmer>
        {error ? (
          <Message negative>
            <Message.Header>
              {i18next.t("Error while fetching timeline events")}
            </Message.Header>
          </Message>
        ) : isFetching ? (
          <Segment basic>
            <Placeholder fluid>
              {Array.from({
                length: events.length < 5 ? 5 : events.length,
              }).map((_, index) => (
                <Placeholder.Header image key={index}>
                  <Placeholder.Line />
                  <Placeholder.Line />
                </Placeholder.Header>
              ))}
            </Placeholder>
          </Segment>
        ) : !_isEmpty(events) ? (
          <Feed>
            {events.map((event) => (
              <TimelineEvent key={event.id} event={event} />
            ))}
          </Feed>
        ) : null}
      </Dimmer.Dimmable>
      <EventSubmitForm request={request} setEvents={setEvents} />
    </>
  );
};

Timeline.propTypes = {
  request: PropTypes.object,
};
