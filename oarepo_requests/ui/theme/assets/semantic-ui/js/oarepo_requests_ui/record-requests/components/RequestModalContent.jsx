import React from "react";
import PropTypes from "prop-types";
import { Grid, List, Form, Divider } from "semantic-ui-react";
import { CustomFields } from "react-invenio-forms";
import {
  SideRequestInfo,
  Timeline,
} from "@js/oarepo_requests_detail/components";

import { REQUEST_MODAL_TYPE } from "../utils/objects";
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

  const renderSubmitForm =
    requestModalType === REQUEST_MODAL_TYPE.SUBMIT_FORM && customFields?.ui;
  const renderReadOnlyData =
    requestModalType === REQUEST_MODAL_TYPE.READ_ONLY && request?.payload;
  const description = request?.stateful_description || request?.description;
  return (
    <Grid doubling stackable>
      <Grid.Row>
        {description && (
          <Grid.Column as="p" id="request-modal-desc">
            {description}
          </Grid.Column>
        )}
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
