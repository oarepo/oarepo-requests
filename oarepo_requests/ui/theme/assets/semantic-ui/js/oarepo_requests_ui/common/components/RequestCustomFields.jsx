import React from "react";
import { Grid, Form, Divider } from "semantic-ui-react";
import { CustomFields } from "react-invenio-forms";
import { REQUEST_MODAL_TYPE } from "@js/oarepo_requests_common";
import PropTypes from "prop-types";
import { useQuery } from "@tanstack/react-query";
import { Formik } from "formik";
import { useFormikRefContext } from "../contexts";
import _isEmpty from "lodash/isEmpty";
import { httpApplicationJson } from "@js/oarepo_ui";

export const RequestCustomFields = ({ request, columnWidth }) => {
  const formikRef = useFormikRefContext();
  console.log("dwadwadwadawdwadawda");
  const { data, isLoading } = useQuery(
    ["applicableCustomFieldssss", request?.type],
    () => httpApplicationJson.get(`/requests/configs/${request?.type}`),
    {
      enabled: !!request?.type,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    }
  );
  console.log("RequestCustomFields data:", data);
  const customFields = data?.data?.custom_fields;
  console.log(customFields, "customFields");
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
      const { read_only_ui_widget } = field;
      return {
        ...field,
        ui_widget: read_only_ui_widget,
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
      customFieldsPaths?.includes(key)
    );
  console.log(renderSubmitForm, renderReadOnlyData, "render flags");
  console.log(request.is_closed, "request.is_closed");
  return renderSubmitForm || renderReadOnlyData ? (
    <Grid.Row>
      <Grid.Column width={columnWidth}>
        {renderSubmitForm && !request.is_closed && (
          <Formik
            initialValues={
              !_isEmpty(request?.payload)
                ? { payload: request.payload }
                : { payload: {} }
            }
            innerRef={formikRef}
          >
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
          </Formik>
        )}

        {renderReadOnlyData && (
          <div className="requests-form-cf">
            <CustomFields
              config={readOnlyCustomFieldsConfig}
              templateLoaders={[
                (widget) => import(`@templates/custom_fields/${widget}.js`),
                (widget) =>
                  import(
                    `@js/oarepo_requests_common/components/DefaultView.jsx`
                  ),
              ]}
              fieldPathPrefix="payload"
            />
          </div>
        )}
      </Grid.Column>
    </Grid.Row>
  ) : null;
};

RequestCustomFields.propTypes = {
  request: PropTypes.object.isRequired,
  customFields: PropTypes.object,
  columnWidth: PropTypes.number,
};

RequestCustomFields.defaultProps = {
  columnWidth: 16,
};
