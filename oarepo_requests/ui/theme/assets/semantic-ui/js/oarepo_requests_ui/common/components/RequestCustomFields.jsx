import React from "react";
import { Grid, List, Form, Divider } from "semantic-ui-react";
import { CustomFields } from "react-invenio-forms";
import {
  ReadOnlyCustomFields,
  REQUEST_TYPE,
  REQUEST_MODAL_TYPE,
} from "@js/oarepo_requests_common";
import PropTypes from "prop-types";

export const RequestCustomFields = ({
  request,
  customFields,
  actions,
  columnWidth,
}) => {
  // Only applies to RequestModalContent component:
  // READ ONLY modal type contains Accept, Decline, and/or Cancel actions OR contains Cancel action only => only ReadOnlyCustomFields are rendered
  // SUBMIT FORM modal type contains Submit and/or Save, Create, CreateAndSubmit action => Form is rendered
  const customFieldsType = actions.some(
    ({ name }) => name === REQUEST_TYPE.ACCEPT || name === REQUEST_TYPE.CANCEL
  )
    ? REQUEST_MODAL_TYPE.READ_ONLY
    : REQUEST_MODAL_TYPE.SUBMIT_FORM;

  const renderSubmitForm =
    customFieldsType === REQUEST_MODAL_TYPE.SUBMIT_FORM &&
    customFields?.ui?.length > 0;
  const customFieldsPaths = customFields?.ui
    ?.map(({ fields }) => {
      let paths = [];
      for (const field of fields) {
        paths.push(field.field);
      }
      return paths;
    })
    .flat();

  const renderReadOnlyData =
    customFieldsType === REQUEST_MODAL_TYPE.READ_ONLY &&
    Object.keys(request?.payload || {}).some((key) =>
      customFieldsPaths?.includes(key)
    );

  return renderSubmitForm || renderReadOnlyData ? (
    <Grid.Row>
      <Grid.Column width={columnWidth}>
        {renderSubmitForm && (
          <Form className="requests-form-cf">
            <CustomFields
              config={customFields?.ui}
              templateLoaders={[
                (widget) => import(`@templates/custom_fields/${widget}.js`),
                () => import(`react-invenio-forms`),
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
                        import(
                          `@js/oarepo_requests_common/widgets/${widget}.jsx`
                        ),
                      () => import(`react-invenio-forms`),
                    ]}
                  />
                </List.Content>
              </List.Item>
            ))}
          </List>
        )}
      </Grid.Column>
    </Grid.Row>
  ) : null;
};

RequestCustomFields.propTypes = {
  request: PropTypes.object.isRequired,
  customFields: PropTypes.object,
  actions: PropTypes.array.isRequired,
  columnWidth: PropTypes.number,
};

RequestCustomFields.defaultProps = {
  columnWidth: 16,
};
