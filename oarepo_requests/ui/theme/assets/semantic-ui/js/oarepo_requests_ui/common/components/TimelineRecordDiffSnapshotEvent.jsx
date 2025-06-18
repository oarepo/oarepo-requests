import React, { useState } from "react";
import PropTypes from "prop-types";
import { Icon, Feed, Table, Message, Accordion } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { toRelativeTime, Image } from "react-invenio-forms";
import _isArray from "lodash/isArray";
import _isObjectLike from "lodash/isObject";
import _every from "lodash/every";
import _isString from "lodash/isString";
import {
  getRequestStatusIcon,
  getFeedMessage,
} from "@js/oarepo_requests_common";

export const TimelineRecordDiffSnapshotEvent = ({ event }) => {
  const [visibleAccordions, setVisibleAccordions] = useState({});

  const eventIcon = getRequestStatusIcon("edited");
  const feedMessage = getFeedMessage("edited");

  const createdBy = event?.expanded?.created_by;
  const creatorLabel =
    createdBy?.profile?.full_name || createdBy?.username || createdBy?.email;

  const toggleAccordion = (operationType) => {
    setVisibleAccordions(prev => ({
      ...prev,
      [operationType]: !prev[operationType]
    }));
  };

  // Parse and process diff data
  const renderDiffTables = () => {
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

      // Group operations by type
      const operationsByType = diffOperations.reduce((groups, op) => {
        const operationType = op.op.toLowerCase();
        if (!groups[operationType]) {
          groups[operationType] = [];
        }
        groups[operationType].push(op);
        return groups;
      }, {});

      // Format values for display
      const formatValue = (value) => {
        if (value === null || value === undefined) return "—";
        if (_isArray(value) && _every(value, _isString)) return value.join(", ");
        if (_isObjectLike(value))
          return JSON.stringify(value, null, 2);
        return String(value);
      };

      // Convert path to human readable format
      const formatPath = (path) => {
        return path
          .replace(/^\//, "")
          .replace(/\/(\d+)\//g, (match, arrayIndex) => {
            return ` › ${parseInt(arrayIndex) + 1} › `;
          })
          .replace(/\/(\d+)$/, (match, arrayIndex) => {
            return ` › ${parseInt(arrayIndex) + 1}`;
          })
          .replace(/\//g, " › ");
      };

      const renderOperationTable = (operations, operationType) => {
        const operationConfig = {
          add: {
            title: i18next.t("Added"),
            icon: "add",
            color: "green"
          },
          remove: {
            title: i18next.t("Removed"),
            icon: "remove",
            color: "red"
          },
          replace: {
            title: i18next.t("Changed"),
            icon: "pencil",
            color: "orange"
          }
        };

        const config = operationConfig[operationType];
        if (!config || operations.length === 0) return null;

        const isVisible = visibleAccordions[operationType] || false;

        return (
          <Accordion key={operationType} fluid className={`operation-accordion ${operationType}`}>
            <Accordion.Title
              active={isVisible}
              onClick={() => toggleAccordion(operationType)}
              className={`operation-title ${operationType}`}
            >
              <Icon name="dropdown" />
              <span>
                <Icon name={config.icon} className="operation-icon" />
                {config.title}
                <span className="operation-count">({operations.length})</span>
              </span>
            </Accordion.Title>
            <Accordion.Content active={isVisible}>
              <Table basic celled stackable className={`record-diff-table requests ${operationType}`}>
                <Table.Header>
                  <Table.Row>
                    <Table.HeaderCell>{i18next.t("Field")}</Table.HeaderCell>
                    {operationType === "replace" ? (
                      <>
                        <Table.HeaderCell>{i18next.t("Old Value")}</Table.HeaderCell>
                        <Table.HeaderCell>{i18next.t("New Value")}</Table.HeaderCell>
                      </>
                    ) : (
                      <Table.HeaderCell>{i18next.t("Value")}</Table.HeaderCell>
                    )}
                  </Table.Row>
                </Table.Header>
                <Table.Body>
                  {operations.map((op, index) => (
                    <Table.Row key={`${operationType}-${index}`}>
                      <Table.Cell>
                        <code>{formatPath(op.path)}</code>
                      </Table.Cell>
                      {operationType === "replace" ? (
                        <>
                          <Table.Cell>
                            <pre>{formatValue(op.old_value)}</pre>
                          </Table.Cell>
                          <Table.Cell>
                            <pre>{formatValue(op.value)}</pre>
                          </Table.Cell>
                        </>
                      ) : (
                        <Table.Cell>
                          <pre>{formatValue(operationType === "remove" ? op.old_value : op.value)}</pre>
                        </Table.Cell>
                      )}
                    </Table.Row>
                  ))}
                </Table.Body>
              </Table>
            </Accordion.Content>
          </Accordion>
        );
      };

      return (
        <div className="diff-tables-container">
          {renderOperationTable(operationsByType.add || [], "add")}
          {renderOperationTable(operationsByType.remove || [], "remove")}
          {renderOperationTable(operationsByType.replace || [], "replace")}
        </div>
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
          <Feed.Extra>
            {renderDiffTables()}
          </Feed.Extra>
        </Feed.Content>
      </Feed.Event>
    </div>
  );
};

TimelineRecordDiffSnapshotEvent.propTypes = {
  event: PropTypes.object.isRequired,
};
