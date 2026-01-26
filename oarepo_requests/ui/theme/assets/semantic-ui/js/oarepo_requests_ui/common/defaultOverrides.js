import { defaultContribComponents } from "@js/invenio_requests/contrib";
import {
  AcceptStatus,
  CancelStatus,
  DeclineStatus,
  DeleteStatus,
  ExpireStatus,
  SubmitStatus,
} from "@js/invenio_requests/request";
import {
  TimelineAcceptEvent,
  TimelineCancelEvent,
  TimelineCommentDeletionEvent,
  TimelineDeclineEvent,
  TimelineExpireEvent,
  TimelineLockRequestEvent,
  TimelineUnlockRequestEvent,
  TimelineUnknownEvent,
  TimelineReviewersUpdatedEvent,
} from "@js/invenio_requests/timelineEvents";
import { i18next } from "@translations/oarepo_requests_ui/i18next";

const defaultComponents = {
  ...defaultContribComponents,
  "TimelineEvent.layout.unknown": TimelineUnknownEvent,
  "TimelineEvent.layout.declined": TimelineDeclineEvent,
  "TimelineEvent.layout.accepted": TimelineAcceptEvent,
  "TimelineEvent.layout.expired": TimelineExpireEvent,
  "TimelineEvent.layout.cancelled": TimelineCancelEvent,
  "TimelineEvent.layout.reviewers_updated": TimelineReviewersUpdatedEvent,
  "TimelineEvent.layout.comment_deleted": TimelineCommentDeletionEvent,
  "TimelineEvent.layout.locked": TimelineLockRequestEvent,
  "TimelineEvent.layout.unlocked": TimelineUnlockRequestEvent,
  "RequestStatus.layout.submitted": SubmitStatus,
  "RequestStatus.layout.deleted": DeleteStatus,
  "RequestStatus.layout.accepted": AcceptStatus,
  "RequestStatus.layout.declined": DeclineStatus,
  "RequestStatus.layout.cancelled": CancelStatus,
  "RequestStatus.layout.expired": ExpireStatus,
  // "RequestActionModalTrigger.create": () => null,
  "RequestActionModal.title.cancel": () => i18next.t("Cancel request"),
  "RequestActionModal.title.accept": () => i18next.t("Accept request"),
  "RequestActionModal.title.decline": () => i18next.t("Decline request"),
  "InvenioRequests.RequestAction": () => null,
};
console.log("oarepo_requests_ui defaultComponents", defaultComponents);

export default defaultComponents;
