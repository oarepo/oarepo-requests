import React, { memo } from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Icon, Feed } from "semantic-ui-react";
import _has from "lodash/has";
import sanitizeHtml from "sanitize-html";
import { hasAll, hasAny, getRequestStatusIcon } from "../utils";
import PropTypes from "prop-types";

const TimelineEvent = ({ event }) => {
  const isRenderable =
    hasAll(event, "created", "payload") &&
    hasAny(event.payload, "event", "content");
  const eventLabel = isRenderable
    ? event.payload?.event ?? i18next.t("commented")
    : null;
  const eventIcon = getRequestStatusIcon(eventLabel) ?? {
    name: "user circle",
    color: "grey",
  };

  return isRenderable ? (
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
          {_has(event, "created_by.label") ? (
            <>
              <Feed.User
                href={event.created_by?.links?.self}
                target="_blank"
                rel="noreferrer"
              >
                {event.created_by.label}
              </Feed.User>{" "}
              {eventLabel} {i18next.t("this request")}
              <Feed.Date>{event.created}</Feed.Date>
            </>
          ) : (
            <>
              {i18next.t("Request")} {eventLabel}
              <Feed.Date>{event.created}</Feed.Date>
            </>
          )}
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
  ) : null;
};

TimelineEvent.propTypes = {
  event: PropTypes.object.isRequired,
};
export default memo(
  TimelineEvent,
  (prevProps, nextProps) => prevProps.event.updated === nextProps.event.updated
);
