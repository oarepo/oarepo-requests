import React from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import TimeLineActionEvent from "@js/invenio_requests/components/TimelineActionEvent";

// placeholder component for escalation as data is not yet available
// to whom the request is escalated etc.
export const TimelineEscalationEvent = ({ event }) => {
  return (
    <TimeLineActionEvent
      event={event}
      iconName="arrow circle up"
      eventContent={i18next.t("escalated")}
    />
  );
};

TimelineEscalationEvent.propTypes = {
  event: PropTypes.object,
};
