import {
  TimelineCommentEvent,
  TimelineActionEvent,
  TimelineEscalationEvent,
  TimelineRecordDiffSnapshotEvent,
} from "@js/oarepo_requests_common";

const overrides = {
  "OarepoRequests.TimelineEvent.C": TimelineCommentEvent,
  "OarepoRequests.TimelineEvent.L": TimelineActionEvent,
  "OarepoRequests.TimelineEvent.E": TimelineEscalationEvent,
  "OarepoRequests.TimelineEvent.S": TimelineRecordDiffSnapshotEvent,
};

export default overrides;
