import React, { memo } from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Feed, Image } from "semantic-ui-react";
import _has from "lodash/has";
import sanitizeHtml from "sanitize-html";
import PropTypes from "prop-types";
import { toRelativeTime } from "react-invenio-forms";

const TimelineCommentEvent = ({ event }) => {
  const createdBy = event?.expanded?.created_by;
  const creatorLabel = createdBy?.username || createdBy?.email;
  return (
    <div className="requests comment-event-container">
      <Feed.Event key={event.id}>
        {createdBy?.links?.avatar && (
          <div className="requests comment-event-avatar">
            <Image
              src={createdBy?.links?.avatar}
              alt={i18next.t("User avatar")}
            />
          </div>
        )}
        <Feed.Content>
          <Feed.Summary>
            <b>{creatorLabel}</b>
            <Feed.Date>
              {i18next.t("requestCommented")}{" "}
              {toRelativeTime(event.created, i18next.language)}
            </Feed.Date>
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
      <div className="comment-event-vertical-line"></div>
    </div>
  );
};

TimelineCommentEvent.propTypes = {
  event: PropTypes.object.isRequired,
};
export default memo(
  TimelineCommentEvent,
  (prevProps, nextProps) => prevProps.event.updated === nextProps.event.updated
);
