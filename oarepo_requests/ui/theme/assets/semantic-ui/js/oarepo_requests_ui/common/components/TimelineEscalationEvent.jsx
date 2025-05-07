import React from "react";
import PropTypes from "prop-types";
import { Icon, Feed } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { toRelativeTime, Image } from "react-invenio-forms";

// placeholder component for escalation as data is not yet available
// to whom the request is escalated etc.
export const TimelineEscalationEvent = ({ event }) => {
  const createdBy = event?.expanded?.created_by;
  const creatorLabel =
    createdBy?.profile?.full_name || createdBy?.username || createdBy?.email;

  return (
    <div className="requests action-event-container">
      <Feed.Event>
        <div className="action-event-vertical-line"></div>
        <Feed.Content>
          <Feed.Summary className="flex align-items-center">
            <div className="flex align-items-center justify-center">
              <Icon
                className="requests action-event-icon"
                name="arrow circle up"
              />
            </div>
            <div className="requests action-event-avatar inline-block">
              <Image
                src={createdBy?.links?.avatar}
                alt={i18next.t("User avatar")}
              />
            </div>
            <b className="ml-5">{creatorLabel}</b>
            <Feed.Date>
              {i18next.t("escalated")}{" "}
              {toRelativeTime(event.updated, i18next.language)}
            </Feed.Date>
          </Feed.Summary>
        </Feed.Content>
      </Feed.Event>
    </div>
  );
};

TimelineEscalationEvent.propTypes = {
  event: PropTypes.object,
};
