// This file is part of React-Invenio-Forms
// Copyright (C) 2022 CERN.
// Copyright (C) 2022 Northwestern University.
//
// React-Invenio-Forms is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { loadWidgetsFromConfig } from "../../utils/loader";
import _has from "lodash/has";
import _zip from "lodash/zip";

const ReadOnlyCustomFields = ({
  config,
  data,
  fieldPathPrefix,
  templateLoaders,
  includesPaths = (fields) => fields.map((field) => field.key)
}) => {
  const [sections, setSections] = useState([]);

  const loadCustomFieldsWidgets = async () => {
    const sections = [];
    for (const sectionCfg of config) {
      const usedFields = sectionCfg.fields.filter((field) => _has(data, field.field));
      const Widgets = await loadWidgetsFromConfig({
        templateLoaders: templateLoaders,
        fieldPathPrefix: fieldPathPrefix,
        fields: usedFields,
      });
      const widgetsWithConfig = _zip(Widgets, usedFields);
      const filteredFieldsWithData = widgetsWithConfig
        .map(([Widget, fieldConfig]) => {
          const value = data[fieldConfig.field];
          return <Widget key={fieldConfig.field} props={fieldConfig.view_widget_props} value={value} />;
        });
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

export default ReadOnlyCustomFields;
