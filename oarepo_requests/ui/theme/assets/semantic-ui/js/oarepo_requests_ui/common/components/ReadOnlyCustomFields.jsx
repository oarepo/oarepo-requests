import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { loadWidgetsFromConfig } from "@js/oarepo_requests_common";
import _has from "lodash/has";
import _zip from "lodash/zip";

export const ReadOnlyCustomFields = ({
  config,
  data,
  fieldPathPrefix,
  templateLoaders,
  includesPaths = (fields) => fields.map((field) => field.key),
}) => {
  const [sections, setSections] = useState([]);

  const loadCustomFieldsWidgets = async () => {
    const sections = [];
    for (const sectionCfg of config) {
      const usedFields = sectionCfg.fields.filter((field) =>
        _has(data, field.field)
      );
      const Widgets = await loadWidgetsFromConfig({
        templateLoaders: templateLoaders,
        fieldPathPrefix: fieldPathPrefix,
        fields: usedFields,
      });
      const widgetsWithConfig = _zip(Widgets, usedFields);
      const filteredFieldsWithData = widgetsWithConfig.map(
        ([Widget, fieldConfig]) => {
          const value = data[fieldConfig.field];
          return (
            <Widget
              key={fieldConfig.field}
              props={fieldConfig.view_widget_props}
              value={value}
            />
          );
        }
      );
      sections.push({ ...sectionCfg, fields: filteredFieldsWithData });
    }
    return sections;
  };

  useEffect(() => {
    loadCustomFieldsWidgets()
      .then((sections) => {
        sections = sections.map((sectionCfg) => {
          const paths = includesPaths(sectionCfg.fields, fieldPathPrefix);
          return { ...sectionCfg, paths };
        });
        setSections(sections);
      })
      .catch((error) => {
        console.error("Couldn't load custom fields widgets.", error);
      });
  }, [config, fieldPathPrefix, includesPaths, templateLoaders]);

  return (
    <>
      {sections.map(({ section, fields, paths }) => (
        <React.Fragment key={section}>{fields}</React.Fragment>
      ))}
    </>
  );
};

ReadOnlyCustomFields.propTypes = {
  config: PropTypes.arrayOf(
    PropTypes.shape({
      section: PropTypes.string.isRequired,
      fields: PropTypes.arrayOf(
        PropTypes.shape({
          field: PropTypes.string.isRequired,
          view_widget: PropTypes.string,
          view_widget_props: PropTypes.object,
        })
      ),
    })
  ),
  data: PropTypes.object.isRequired, // { field1: value1, field2: value2, ...} just like Formik initialValues
  templateLoaders: PropTypes.array.isRequired,
  fieldPathPrefix: PropTypes.string,
  includesPaths: PropTypes.func,
};

ReadOnlyCustomFields.defaultProps = {
  includesPaths: (fields) => fields.map((field) => field.key),
};
