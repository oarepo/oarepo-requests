import React from "react";
import Overridable from "react-overridable";
import {
  TimelineCommentEvent,
  TimelineActionEvent,
} from "@js/oarepo_requests_common";
import PropTypes from "prop-types";

export const TimelineEvent = ({ event }) => (
  <React.Fragment>
    {event.type === "C" && (
      <Overridable id="OarepoRequests.TimelineCommentEvent" event={event}>
        <TimelineCommentEvent event={event} />
      </Overridable>
    )}
    {event.type === "L" && (
      <Overridable
        id={`OarepoRequests.TimelineActionEvent.${event.payload.event}`}
        event={event}
      >
        <TimelineActionEvent event={event} />
      </Overridable>
    )}
  </React.Fragment>
);

TimelineEvent.propTypes = {
  event: PropTypes.object,
};
