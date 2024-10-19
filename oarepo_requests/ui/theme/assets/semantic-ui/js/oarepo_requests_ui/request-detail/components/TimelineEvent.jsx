import React, { memo } from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Icon, Feed } from "semantic-ui-react";
import _has from "lodash/has";
import sanitizeHtml from "sanitize-html";
import {
  getRequestStatusIcon,
  getFeedMessage,
} from "@js/oarepo_requests_common";
import PropTypes from "prop-types";

const TimelineEvent = ({ event }) => {
  const eventLabel = event.payload?.event ?? i18next.t("commented");
  console.log(eventLabel);
  const eventIcon = getRequestStatusIcon(eventLabel) ?? {
    name: "user circle",
    color: "grey",
  };
  const creatorLabel = event.created_by?.label;
  const feedMessage = getFeedMessage(eventLabel, creatorLabel);
  return (
    <Feed.Event key={event.id}>
      <Feed.Label>
        <Icon
          name={eventIcon.name}
          color={eventIcon.color}
          aria-label={`${eventLabel} ${i18next.t("icon")}`}
        />
      </Feed.Label>
      <Feed.Content>
        <Feed.Summary>
          {feedMessage}
          <Feed.Date>{event.created}</Feed.Date>
        </Feed.Summary>
        {_has(event.payload, "content") && (
          <Feed.Extra text>
            <div
              dangerouslySetInnerHTML={{
                __html: sanitizeHtml(event.payload.content),
              }}
            />
          </Feed.Extra>
        )}
      </Feed.Content>
    </Feed.Event>
  );
};

TimelineEvent.propTypes = {
  event: PropTypes.object.isRequired,
};
export default memo(
  TimelineEvent,
  (prevProps, nextProps) => prevProps.event.updated === nextProps.event.updated
);
