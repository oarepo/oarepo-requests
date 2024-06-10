import React, { memo } from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Icon, Feed } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import _sortBy from "lodash/sortBy";
import _has from "lodash/has";
import { hasAll, hasAny, sanitizeInput } from "../utils";

const TimelineEvent = ({ event }) => {
  const isRenderable = hasAll(event, 'created', 'payload') && hasAny(event.payload, 'event', 'content');
  const eventLabel = isRenderable ? event.payload?.event ?? i18next.t("commented") : null;
  return isRenderable ? (            
    <Feed.Event key={event.id}>
      <Feed.Label>
        <Icon name='user circle' aria-label={i18next.t('User icon')} />
      </Feed.Label>
      <Feed.Content>
        <Feed.Summary>
          {_has(event, "created_by.user") ? 
            <><Feed.User>{event.created_by.user}</Feed.User> {eventLabel} this request on<Feed.Date>{event.created}</Feed.Date></> : 
            <span>Request {eventLabel} on {event.created}</span>
          } 
        </Feed.Summary>
        {_has(event.payload, "content") && 
          <Feed.Extra text>
            <div dangerouslySetInnerHTML={{ __html: sanitizeInput(event.payload.content) }} />
          </Feed.Extra>
        }
      </Feed.Content>
    </Feed.Event>
  ) : null;
};

export default memo(TimelineEvent, (prevProps, nextProps) => prevProps.event.updated === nextProps.event.updated);
