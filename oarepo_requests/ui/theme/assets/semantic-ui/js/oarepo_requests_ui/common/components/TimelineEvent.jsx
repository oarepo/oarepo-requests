import React from "react";
import Overridable, { overrideStore } from "react-overridable";
import PropTypes from "prop-types";

export const TimelineEvent = ({ event, requestId, page }) => {
  const overridableId = `OarepoRequests.TimelineEvent.${event.type}`;
  if (!(overridableId in overrideStore.getAll())) {
    console.warn(`No UI component for event type ${event.type}`);
  }
  return (
    <Overridable
      id={overridableId}
      event={event}
      requestId={requestId}
      page={page}
    ></Overridable>
  );
};

TimelineEvent.propTypes = {
  event: PropTypes.object.isRequired,
  requestId: PropTypes.string.isRequired,
  page: PropTypes.number.isRequired,
};
