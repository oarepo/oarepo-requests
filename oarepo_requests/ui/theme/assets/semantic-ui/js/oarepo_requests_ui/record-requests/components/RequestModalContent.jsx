import React, { useEffect, useContext } from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Grid, List, Form, Divider, Comment } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import _sortBy from "lodash/sortBy";
import { useFormikContext } from "formik";

import { CustomFields } from "react-invenio-forms";

import { RequestModal, ModalContentSideInfo } from ".";
import { RequestContext } from "../contexts";
import { REQUEST_TYPE } from "../utils/objects";
import ReadOnlyCustomFields from "./common/ReadOnlyCustomFields";

/** 
 * @typedef {import("../types").Request} Request
 * @typedef {import("../types").RequestType} RequestType
 * @typedef {import("../types").RequestTypeEnum} RequestTypeEnum
 * @typedef {import("../types").Event} Event
 */

/** @param {{ request: Request, requestModalType: RequestTypeEnum, requestType: RequestType, fetchNewEvents: (url: string, setter: (events: Event[]) => void) => Promise<Event>, customSubmitHandler: (e) => void }} props */
export const RequestModalContent = ({ request, requestType, requestModalType, fetchNewEvents, customSubmitHandler }) => {
  /** @type {[Request[], (requests: Request[]) => void]} */
  const { requests, setRequests } = useContext(RequestContext);

  const actualRequest = requests.find(req => req.id === request.id);

  useEffect(() => {
    if (!_isEmpty(request.links?.events)) {
      fetchNewEvents(request.links.events, (events) => {
        setRequests(requests => requests.map(req => {
          if (req.id === request.id) {
            req.events = events;
          }
          return req;
        }));
      });
    }
  }, [actualRequest]);

  const { handleSubmit } = useFormikContext();

  const onSubmit = (event) => {
    if (_isFunction(customSubmitHandler)) {
      customSubmitHandler(event?.nativeEvent?.submitter?.name);
    } else {
      handleSubmit(event);
    }
  }

  const payloadUI = requestType?.payload_ui;
  const eventTypes = requestType?.event_types;

  /** @type {Event[]} */
  let events = [];
  if (!_isEmpty(request?.events)) {
    events = _sortBy(request.events, ['updated']);
  } else if (!_isEmpty(actualRequest?.events)) {
    events = _sortBy(actualRequest.events, ['updated']);
  }

  const renderSubmitForm = requestModalType === REQUEST_TYPE.SUBMIT && payloadUI;
  const renderReadOnlyData = (requestModalType === REQUEST_TYPE.ACCEPT || requestModalType === REQUEST_TYPE.CANCEL) && request?.payload;

  return (
    <Grid doubling stackable>
      <Grid.Row>
        <Grid.Column as="p" id="request-modal-desc">
          {request.description}
        </Grid.Column>
      </Grid.Row>
      {(renderSubmitForm || renderReadOnlyData) &&
        <Grid.Row>
          <Grid.Column width={3} only="mobile">
            <ModalContentSideInfo request={request} requestType={requestType} isSidebar />
          </Grid.Column>
          <Grid.Column width={13}>
            {renderSubmitForm &&
              <Form onSubmit={onSubmit} id="request-form">
                <CustomFields
                  className="requests-form-cf"
                  config={payloadUI}
                  templateLoaders={[
                    (widget) => import(`@templates/custom_fields/${widget}.js`),
                    (widget) => import(`react-invenio-forms`)
                  ]}
                  fieldPathPrefix="payload"
                />
                <Divider hidden />
              </Form>
            }
            {/* Render read only data for Accept and Cancel modals */}
            {renderReadOnlyData &&
              <>
                <List relaxed>
                  {Object.keys(request.payload).map(key => (
                    <List.Item key={key}>
                      <List.Content>
                        <List.Header>{key}</List.Header>
                        <ReadOnlyCustomFields
                          className="requests-form-cf"
                          config={payloadUI}
                          data={{ [key]: request.payload[key] }}
                          templateLoaders={[
                            (widget) => import(`../components/common/${widget}.jsx`),
                            (widget) => import(`react-invenio-forms`)
                          ]}
                        />
                      </List.Content>
                    </List.Item>
                  ))}
                </List>
                {/* If events are enabled for this request type, you can see the timeline of events and create new events. */}
                {!_isEmpty(eventTypes) &&
                  <>
                    <Divider horizontal>{i18next.t("Timeline")}</Divider>
                    {!_isEmpty(events) &&
                      <Comment.Group>
                        {events.map(event => {
                          const eventPayloadUI = eventTypes.filter(eventType => eventType.id === event.type_code)[0]?.payload_ui;
                          return (
                            <Comment key={event.id}>
                              <Comment.Content>
                                <Comment.Author as="a" href={event.created_by?.link}>{event.created_by.label}</Comment.Author>
                                <Comment.Metadata>
                                  <div>{new Date(event?.created)?.toLocaleString("cs-CZ")}</div>
                                </Comment.Metadata>
                                <Comment.Text>
                                  <ReadOnlyCustomFields
                                    className="requests-events-read-only-cf"
                                    config={eventPayloadUI}
                                    data={event.payload}
                                    templateLoaders={[
                                      (widget) => import(`./${widget}.jsx`),
                                      (widget) => import(`react-invenio-forms`)
                                    ]}
                                  // fieldPathPrefix="payload"
                                  />
                                </Comment.Text>
                              </Comment.Content>
                            </Comment>
                          )
                        })}
                      </Comment.Group>
                    }
                    {eventTypes.map(event => (
                      <RequestModal key={event.id} request={event} requestModalType={REQUEST_TYPE.CREATE} isEventModal
                        triggerButton={<Button key={event.id} compact primary icon="plus" labelPosition="left" content={event.name} />} />
                    ))}
                  </>
                }
              </>
            }
          </Grid.Column>
          <Grid.Column width={3} only="tablet computer">
            <ModalContentSideInfo request={request} requestType={requestType} isSidebar />
          </Grid.Column>
        </Grid.Row> ||
        /* No Submit Form (no PayloadUI for this request type) nor Payload (read only data) available for this Request */
        <Grid.Row>
          <Grid.Column>
            <ModalContentSideInfo request={request} requestType={requestType} isSidebar={false} />
          </Grid.Column>
        </Grid.Row>
      }
    </Grid>
  );
}

RequestModalContent.propTypes = {
  request: PropTypes.object.isRequired,
  requestType: PropTypes.object.isRequired,
};