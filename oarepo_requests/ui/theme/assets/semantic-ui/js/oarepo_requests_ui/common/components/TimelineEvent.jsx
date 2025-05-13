import React from "react";
import Overridable from "react-overridable";
import PropTypes from "prop-types";
import { GenericActionEvent } from "./GenericActionEvent";

export const TimelineEvent = ({ event, requestId, page }) => (
  <Overridable
    id={`OarepoRequests.TimelineEvent.${event.type}`}
    event={event}
    requestId={requestId}
    page={page}
  >
    <GenericActionEvent
      event={event}
      eventIcon={{ name: "info" }}
      feedMessage={`No UI component for event type ${event.type}`}
    />
  </Overridable>
);

TimelineEvent.propTypes = {
  event: PropTypes.object.isRequired,
  requestId: PropTypes.string.isRequired,
  page: PropTypes.number.isRequired,
};
