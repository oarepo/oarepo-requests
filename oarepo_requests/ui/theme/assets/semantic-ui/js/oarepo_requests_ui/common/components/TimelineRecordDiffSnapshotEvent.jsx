import React from "react";
import PropTypes from "prop-types";
import { Icon, Feed, Table, Label, Message } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { toRelativeTime, Image } from "react-invenio-forms";
import _isArray from "lodash/isArray";
import _isObjectLike from "lodash/isObject";
import {
  getRequestStatusIcon,
  getFeedMessage,
} from "@js/oarepo_requests_common";

export const TimelineRecordDiffSnapshotEvent = ({ event }) => {
  const eventIcon = getRequestStatusIcon("edited");
  const feedMessage = getFeedMessage("edited");

  const createdBy = event?.expanded?.created_by;
  const creatorLabel =
    createdBy?.profile?.full_name || createdBy?.username || createdBy?.email;

  // Parse and process diff data
  const renderDiffTable = () => {
    if (!event.payload?.diff) return null;

    try {
      const diffOperations = JSON.parse(event.payload.diff);

      if (!_isArray(diffOperations)) {
        return null;
      }

      // Handle case where there are no changes
      if (diffOperations.length === 0) {
        return (
          <div>
            <Icon name="info circle" />
            {i18next.t("No changes detected between versions")}
          </div>
        );
      }

      // Group operations by base path for better organization
      const groupedOperations = diffOperations.reduce((groups, op) => {
        const basePath = op.path.split("/")[1] || op.path; // Get first level path
        if (!groups[basePath]) {
          groups[basePath] = [];
        }
        groups[basePath].push(op);
        return groups;
      }, {});

      return (
        <Table basic collapsing celled className="requests record-diff-table">
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell width={3}>{i18next.t("Field")}</Table.HeaderCell>
              <Table.HeaderCell width={2}>{i18next.t("Operation")}</Table.HeaderCell>
              <Table.HeaderCell width={5}>{i18next.t("Old Value")}</Table.HeaderCell>
              <Table.HeaderCell width={5}>{i18next.t("New Value")}</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {Object.entries(groupedOperations).map(([basePath, operations]) =>
              operations.map((op, index) => {
                // Convert 0-based array indices to 1-based for human readability
                const humanReadablePath = op.path
                  .replace(/^\//, "")
                  .replace(/\/(\d+)\//g, (match, arrayIndex) => {
                    return `/${parseInt(arrayIndex) + 1}/`;
                  })
                  .replace(/\/(\d+)$/, (match, arrayIndex) => {
                    return `/${parseInt(arrayIndex) + 1}`;
                  })
                  .replace(/\//g, " › ");
                
                const operationType = op.op.toLowerCase();

                // Format values for display
                const formatValue = (value) => {
                  if (value === null || value === undefined) return "—";
                  if (_isArray(value)) return value.join(", ");
                  if (_isObjectLike(value))
                    return JSON.stringify(value, null, 2);
                  return String(value);
                };

                const getOperationColor = (operation) => {
                  switch (operation.toLowerCase()) {
                    case "add":
                      return "green";
                    case "remove":
                      return "red";
                    case "replace":
                      return "orange";
                    default:
                      return "grey";
                  }
                };

                return (
                  <Table.Row key={`${basePath}-${index}`}>
                    <Table.Cell>
                      <code>{humanReadablePath}</code>
                    </Table.Cell>
                    <Table.Cell>
                      <Label
                        color={getOperationColor(operationType)}
                        size="small"
                      >
                        {i18next.t(operationType).toUpperCase()}
                      </Label>
                    </Table.Cell>
                    <Table.Cell>
                      {operationType === "add" ? (
                        <em>{i18next.t("None")}</em>
                      ) : (
                        <pre>
                          {formatValue(op.old_value)}
                        </pre>
                      )}
                    </Table.Cell>
                    <Table.Cell>
                      {operationType === "remove" ? (
                        <em>{i18next.t("Removed")}</em>
                      ) : (
                        <pre>
                          {formatValue(op.value)}
                        </pre>
                      )}
                    </Table.Cell>
                  </Table.Row>
                );
              })
            )}
          </Table.Body>
        </Table>
      );
    } catch (error) {
      return (
        <Message negative>
          <Message.Header>
            {i18next.t("Unable to parse diff data")}
          </Message.Header>
          <p>{i18next.t("There was an error processing the diff data.")}</p>
          {error?.message && <pre>{error.message}</pre>}
        </Message>
      );
    }
  };

  return (
    <div className="requests action-event-container">
      <Feed.Event>
        <div className="action-event-vertical-line"></div>
        <Feed.Content>
          <Feed.Summary className="flex align-items-center">
            <div className="flex align-items-center justify-center">
              <Icon
                className="requests action-event-icon"
                name={eventIcon?.name}
                color={eventIcon?.color}
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
              {feedMessage} {toRelativeTime(event.updated, i18next.language)}
            </Feed.Date>
          </Feed.Summary>
          <Feed.Extra>{renderDiffTable()}</Feed.Extra>
        </Feed.Content>
      </Feed.Event>
    </div>
  );
};

TimelineRecordDiffSnapshotEvent.propTypes = {
  event: PropTypes.object,
  eventIcon: PropTypes.object,
  feedMessage: PropTypes.string,
};
