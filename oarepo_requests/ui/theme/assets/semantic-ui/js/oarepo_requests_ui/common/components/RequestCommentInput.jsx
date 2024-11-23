import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { FormField } from "semantic-ui-react";
import { RichInputField, FieldLabel, RichEditor } from "react-invenio-forms";
import { useFormikContext } from "formik";
import sanitizeHtml from "sanitize-html";
import PropTypes from "prop-types";

export const RequestCommentInput = ({ fieldPath, label }) => {
  const { values, setFieldValue, setFieldTouched } = useFormikContext();
  return (
    <FormField>
      <RichInputField
        fieldPath={fieldPath}
        label={
          label ? (
            <FieldLabel
              htmlFor={fieldPath}
              label={label}
              className="rel-mb-25"
            />
          ) : null
        }
        optimized="true"
        placeholder={i18next.t("Your comment here...")}
        editor={
          <RichEditor
            initialValue={values?.payload?.content}
            inputValue={() => values?.payload?.content}
            optimized
            editorConfig={{
              auto_focus: true,
              min_height: 100,
              toolbar:
                "blocks | bold italic | bullist numlist | outdent indent | undo redo",
            }}
            onBlur={(event, editor) => {
              const cleanedContent = sanitizeHtml(editor.getContent());
              setFieldValue(fieldPath, cleanedContent);
              setFieldTouched(fieldPath, true);
            }}
          />
        }
      />
    </FormField>
  );
};

RequestCommentInput.propTypes = {
  fieldPath: PropTypes.string,
  label: PropTypes.string,
};

RequestCommentInput.defaultProps = {
  fieldPath: "payload.content",
  label: i18next.t("Comment"),
};
