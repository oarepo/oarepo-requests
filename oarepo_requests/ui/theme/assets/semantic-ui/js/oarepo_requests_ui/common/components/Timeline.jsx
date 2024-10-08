import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Message, Feed, Dimmer, Loader } from "semantic-ui-react";
import {
  EventSubmitForm,
  TimelineEvent,
} from "../../request-detail/components";
import PropTypes from "prop-types";
import { http } from "@js/oarepo_ui";
import { useQuery } from "@tanstack/react-query";

export const Timeline = ({ request }) => {
  const { data, error, isFetching } = useQuery(
    ["requestEvents"],
    () => http.get(request.links?.timeline),
    {
      enabled: !!request.links?.timeline,
      refetchOnWindowFocus: false,
    }
  );
  const events = data?.data?.hits?.hits;
  return (
    <Dimmer.Dimmable blurring dimmed={isFetching}>
      <Dimmer active={isFetching} inverted>
        <Loader indeterminate size="big">
          {i18next.t("Loading timeline...")}
        </Loader>
      </Dimmer>
      {error && (
        <Message negative>
          <Message.Header>
            {i18next.t("Error while fetching timeline events")}
          </Message.Header>
        </Message>
      )}
      {events?.length > 0 && (
        <Feed>
          {events.map((event) => (
            <TimelineEvent key={event.id} event={event} />
          ))}
        </Feed>
      )}
      <EventSubmitForm request={request} />
    </Dimmer.Dimmable>
  );
};

Timeline.propTypes = {
  request: PropTypes.object,
};
