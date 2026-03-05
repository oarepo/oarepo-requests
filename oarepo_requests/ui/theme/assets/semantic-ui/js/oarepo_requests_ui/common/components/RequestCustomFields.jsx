import React from "react";
import { Grid, Form, Divider } from "semantic-ui-react";
import { CustomFields } from "react-invenio-forms";
import PropTypes from "prop-types";
import { Formik } from "formik";
import { useFormikRefContext, useRequestConfigContext } from "../contexts";
import _isEmpty from "lodash/isEmpty";
import { REQUEST_MODAL_TYPE } from "../utils/objects";

export const RequestCustomFields = ({ request, columnWidth }) => {
  const formikRef = useFormikRefContext();
  const { requestTypeConfig } = useRequestConfigContext();

  const customFields = requestTypeConfig?.custom_fields;
  const customFieldsType =
    request.status === "created"
      ? REQUEST_MODAL_TYPE.SUBMIT_FORM
      : REQUEST_MODAL_TYPE.READ_ONLY;
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

  const readOnlyCustomFieldsConfig = customFields?.ui.map((section) => {
    const { fields } = section;
    const fieldsWithReadOnlyWidget = fields.map((field) => {
      const { read_only_ui_widget: readOnlyUiWidget } = field;
      return {
        ...field,
        ui_widget: readOnlyUiWidget,
      };
    });
    return {
      ...section,
      fields: fieldsWithReadOnlyWidget,
    };
  });

  const renderReadOnlyData =
    customFieldsType === REQUEST_MODAL_TYPE.READ_ONLY &&
    Object.keys(request?.payload || {}).some((key) =>
      customFieldsPaths?.includes(key),
    );
  return renderSubmitForm || renderReadOnlyData ? (
    <Formik
      initialValues={
        _isEmpty(request?.payload)
          ? { payload: {} }
          : { payload: request.payload }
      }
      innerRef={formikRef}
    >
      <Grid.Row>
        <Grid.Column width={columnWidth}>
          {renderSubmitForm && !request.is_closed && (
            <Form>
              <div className="requests-form-cf">
                <CustomFields
                  config={customFields?.ui}
                  templateLoaders={[
                    (widget) => import(`@templates/custom_fields/${widget}.js`),
                    () => import(`react-invenio-forms`),
                  ]}
                  fieldPathPrefix="payload"
                />
                <Divider hidden />
              </div>
            </Form>
          )}

          {renderReadOnlyData && (
            <div className="requests-form-cf">
              <CustomFields
                config={readOnlyCustomFieldsConfig}
                templateLoaders={[
                  (widget) => import(`@templates/custom_fields/${widget}.js`),
                  (widget) => import(`./DefaultView.jsx`),
                ]}
                fieldPathPrefix="payload"
              />
            </div>
          )}
        </Grid.Column>
      </Grid.Row>
    </Formik>
  ) : null;
};

RequestCustomFields.propTypes = {
  request: PropTypes.object.isRequired,
  columnWidth: PropTypes.number,
};

RequestCustomFields.defaultProps = {
  columnWidth: 16,
};
