import React from "react";
import Overridable from "react-overridable";
import PropTypes from "prop-types";

export const TimelineEvent = ({ event, requestId, page }) => (
  <Overridable
    id={`OarepoRequests.TimelineEvent.${event.type}`}
    event={event}
    requestId={requestId}
    page={page}
  >
    <div>{`you have not provided UI for event type ${event.type}`}</div>
  </Overridable>
);

TimelineEvent.propTypes = {
  event: PropTypes.object.isRequired,
  requestId: PropTypes.string.isRequired,
  page: PropTypes.number.isRequired,
};
