import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { FormField } from "semantic-ui-react";
import { RichInputField, FieldLabel, RichEditor } from "react-invenio-forms";
import { useFormikContext } from "formik";
import sanitizeHtml from "sanitize-html";

export const RequestCommentInput = () => {
  const {
    values = undefined,
    setFieldValue = undefined,
    setFieldTouched = undefined,
  } = useFormikContext() || {};
  return (
    <FormField>
      <RichInputField
        fieldPath="payload.content"
        label={
          <FieldLabel
            htmlFor="payload.content"
            label={`${i18next.t("Add comment")} (${i18next.t("optional")})`}
            className="rel-mb-25"
          />
        }
        optimized="true"
        placeholder={i18next.t("Your comment here...")}
        editor={
          <RichEditor
            value={values?.payload?.content}
            optimized
            onBlur={(event, editor) => {
              const cleanedContent = sanitizeHtml(editor.getContent());
              setFieldValue("payload.content", cleanedContent);
              setFieldTouched("payload.content", true);
            }}
          />
        }
      />
    </FormField>
  );
};
