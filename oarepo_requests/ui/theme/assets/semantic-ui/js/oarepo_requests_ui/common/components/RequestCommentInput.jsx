import React from "react";
import { RichEditor } from "react-invenio-forms";
import sanitizeHtml from "sanitize-html";
import PropTypes from "prop-types";
import { useQueryClient } from "@tanstack/react-query";

export const RequestCommentInput = ({
  comment,
  handleChange,
  initialValue,
}) => {
  // when focused move the cursor at the end of any existing content
  const handleFocus = (event, editor) => {
    editor.selection.select(editor.getBody(), true);
    editor.selection.collapse(false);
  };

  const queryClient = useQueryClient();
  // the request for request specific info, shall be already fetched at this point
  const data = queryClient.getQueriesData({
    queryKey: ["applicableCustomFields"],
  });

  let allowedHtmlAttrs;
  let allowedHtmlTags;
  if (data.length > 0) {
    allowedHtmlAttrs = data[0][1]?.data?.allowedHtmlAttrs;
    allowedHtmlTags = data[0][1]?.data?.allowedHtmlTags;
  }

  return (
    <RichEditor
      initialValue={initialValue}
      inputValue={comment}
      editorConfig={{
        auto_focus: true,
        min_height: 100,
        toolbar:
          "blocks | bold italic | bullist numlist | outdent indent | undo redo",
      }}
      onEditorChange={(event, editor) => {
        const cleanedContent = sanitizeHtml(editor.getContent(), {
          allowedTags: allowedHtmlTags,
          allowedAttributes: allowedHtmlAttrs,
        });
        handleChange(event, cleanedContent);
      }}
      onFocus={handleFocus}
    />
  );
};

RequestCommentInput.propTypes = {
  comment: PropTypes.string,
  handleChange: PropTypes.func,
  initialValue: PropTypes.string,
};

RequestCommentInput.defaultProps = {
  initialValue: "",
};
