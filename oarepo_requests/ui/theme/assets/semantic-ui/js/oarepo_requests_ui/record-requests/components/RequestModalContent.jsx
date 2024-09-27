import React, { useEffect } from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Grid, List, Form, Divider, Comment } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import _sortBy from "lodash/sortBy";
import { CustomFields } from "react-invenio-forms";
import {
  SideRequestInfo,
  Timeline,
} from "@js/oarepo_requests_detail/components";

import { CreateRequestModalContent, RequestModal } from ".";
import { SubmitEvent } from "./actions";
import { useRequestContext } from "../contexts";
import { fetchUpdated as fetchNewEvents } from "../utils";
import { REQUEST_TYPE, REQUEST_MODAL_TYPE } from "../utils/objects";
import ReadOnlyCustomFields from "./common/ReadOnlyCustomFields";

/**
 * @typedef {import("../types").Request} Request
 * @typedef {import("../types").RequestTypeEnum} RequestTypeEnum
 * @typedef {import("../types").Event} Event
 */

/** @param {{ request: Request, requestModalType: RequestTypeEnum, }} props */
export const RequestModalContent = ({
  request,
  requestModalType,
  customFields,
}) => {
  /** @type {{requests: Request[], setRequests: (requests: Request[]) => void}} */
  const { requests, setRequests } = useRequestContext();
  const actualRequest = requests.find((req) => req.id === request.id);
  useEffect(() => {
    if (!_isEmpty(request.links?.events)) {
      fetchNewEvents(
        request.links.events,
        (responseData) => {
          setRequests((requests) =>
            requests.map((req) => {
              if (req.id === request.id) {
                req.events = responseData?.hits?.hits ?? [];
              }
              return req;
            })
          );
        },
        (error) => {
          console.error(error);
        }
      );
    }
  }, [setRequests, request.links?.events, request.id]);

  // This function can only be triggered if submit form is rendered

  const eventTypes = request?.event_types;
  /** @type {Event[]} */
  let events = [];
  if (!_isEmpty(request?.events)) {
    events = _sortBy(request.events, ["updated"]);
  } else if (!_isEmpty(actualRequest?.events)) {
    events = _sortBy(actualRequest.events, ["updated"]);
  }

  const renderSubmitForm =
    requestModalType === REQUEST_MODAL_TYPE.SUBMIT_FORM && customFields?.ui;
  const renderReadOnlyData =
    requestModalType === REQUEST_MODAL_TYPE.READ_ONLY && request?.payload;
  return (
    <Grid doubling stackable>
      <Grid.Row>
        <Grid.Column as="p" id="request-modal-desc">
          {request.description}
        </Grid.Column>
      </Grid.Row>
      <Grid.Row>
        <Grid.Column>
          <SideRequestInfo request={request} />
        </Grid.Column>
      </Grid.Row>
      {(renderSubmitForm || renderReadOnlyData) && (
        <Grid.Row>
          <Grid.Column width={16}>
            {renderSubmitForm && (
              <Form>
                <CustomFields
                  className="requests-form-cf"
                  config={customFields?.ui}
                  templateLoaders={[
                    (widget) => import(`@templates/custom_fields/${widget}.js`),
                    (widget) => import(`react-invenio-forms`),
                  ]}
                  fieldPathPrefix="payload"
                />
                <Divider hidden />
              </Form>
            )}

            {renderReadOnlyData && (
              <>
                <List relaxed>
                  {Object.keys(request.payload).map((key) => (
                    <List.Item key={key}>
                      <List.Content>
                        <List.Header>{key}</List.Header>
                        <ReadOnlyCustomFields
                          className="requests-form-cf"
                          config={customFields?.ui}
                          data={{ [key]: request.payload[key] }}
                          templateLoaders={[
                            (widget) =>
                              import(`../components/common/${widget}.jsx`),
                            (widget) => import(`react-invenio-forms`),
                          ]}
                        />
                      </List.Content>
                    </List.Item>
                  ))}
                </List>
                {!_isEmpty(eventTypes) && (
                  <>
                    <Divider horizontal>{i18next.t("Timeline")}</Divider>

                    {!_isEmpty(events) && (
                      <Comment.Group>
                        {events.map((event) => {
                          const eventPayloadUI = eventTypes.filter(
                            (eventType) => eventType.id === event.type_code
                          )[0]?.payload_ui;
                          return (
                            <Comment key={event.id}>
                              <Comment.Content>
                                <Comment.Author
                                  as="a"
                                  href={event.created_by?.link}
                                >
                                  {event.created_by.label}
                                </Comment.Author>
                                <Comment.Metadata>
                                  <div>{event?.created}</div>
                                </Comment.Metadata>
                                <Comment.Text>
                                  <ReadOnlyCustomFields
                                    className="requests-events-read-only-cf"
                                    config={eventPayloadUI}
                                    data={event.payload}
                                    templateLoaders={[
                                      (widget) => import(`./${widget}.jsx`),
                                      (widget) => import(`react-invenio-forms`),
                                    ]}
                                  />
                                </Comment.Text>
                              </Comment.Content>
                            </Comment>
                          );
                        })}
                      </Comment.Group>
                    )}

                    {eventTypes.map((event) => (
                      <RequestModal
                        key={event.id}
                        request={event}
                        requestType={event}
                        header={
                          !_isEmpty(event?.title)
                            ? event.title
                            : !_isEmpty(event?.name)
                            ? event.name
                            : event.type
                        }
                        triggerButton={
                          <Button
                            compact
                            primary
                            icon="plus"
                            labelPosition="left"
                            content={event.name}
                          />
                        }
                        actions={[
                          {
                            name: REQUEST_TYPE.CREATE,
                            component: SubmitEvent,
                          },
                        ]}
                        ContentComponent={CreateRequestModalContent}
                      />
                    ))}
                  </>
                )}
              </>
            )}
            <Timeline request={request} />
          </Grid.Column>
        </Grid.Row>
      )}
    </Grid>
  );
};

RequestModalContent.propTypes = {
  request: PropTypes.object.isRequired,
  requestModalType: PropTypes.string.isRequired,
  customFields: PropTypes.object,
};
