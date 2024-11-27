import React, { useState } from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Message, Feed, Dimmer, Loader, Pagination } from "semantic-ui-react";
import {
  EventSubmitForm,
  TimelineEvent,
} from "@js/oarepo_requests_detail/components";
import PropTypes from "prop-types";
import { httpVnd } from "@js/oarepo_ui";
import { useQuery } from "@tanstack/react-query";

export const Timeline = ({ request, timelinePageSize }) => {
  const [page, setPage] = useState(1);
  const { data, error, isLoading, refetch } = useQuery(
    ["requestEvents", request.id, page],
    () =>
      // q=!(type:T) to eliminate system created events
      httpVnd.get(
        `${request.links?.timeline}?q=!(type:T)&page=${page}&size=${timelinePageSize}&sort=newest`
      ),
    {
      enabled: !!request.links?.timeline,
      // when you click on rich editor and then back to the window, it considers
      // that this is focus on the window itself, so unable to use refetchOnWindowFocus
      refetchOnWindowFocus: false,
      refetchInterval: 10000,
    }
  );
  const handlePageChange = (activePage) => {
    if (activePage === page) return;
    setPage(activePage);
  };
  const events = data?.data?.hits?.hits;
  const totalPages = Math.ceil(data?.data?.hits?.total / timelinePageSize);
  return (
    <Dimmer.Dimmable blurring dimmed={isLoading}>
      <Dimmer active={isLoading} inverted>
        <Loader indeterminate size="big">
          {i18next.t("Loading timeline...")}
        </Loader>
      </Dimmer>
      <div className="rel-mb-5">
        <EventSubmitForm
          request={request}
          refetch={refetch}
          page={page}
          timelinePageSize={timelinePageSize}
        />
      </div>
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
      {data?.data?.hits?.total > timelinePageSize && (
        <div className="centered rel-mb-1">
          <Pagination
            size="mini"
            activePage={page}
            totalPages={totalPages}
            onPageChange={(_, { activePage }) => handlePageChange(activePage)}
            ellipsisItem={null}
            firstItem={null}
            lastItem={null}
          />
        </div>
      )}
    </Dimmer.Dimmable>
  );
};

Timeline.propTypes = {
  request: PropTypes.object,
  timelinePageSize: PropTypes.number,
};

Timeline.defaultProps = {
  timelinePageSize: 25,
};
