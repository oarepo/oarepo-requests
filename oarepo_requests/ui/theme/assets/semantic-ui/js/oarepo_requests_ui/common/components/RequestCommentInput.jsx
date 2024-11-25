import React from "react";
import { RichEditor } from "react-invenio-forms";
import sanitizeHtml from "sanitize-html";
import PropTypes from "prop-types";

export const RequestCommentInput = ({
  comment,
  handleChange,
  initialValue,
}) => {
  const handleFocus = (event, editor) => {
    editor.selection.select(editor.getBody(), true);
    editor.selection.collapse(false);
  };

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
        console.log(editor.getContent());
        const cleanedContent = sanitizeHtml(editor.getContent());
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
