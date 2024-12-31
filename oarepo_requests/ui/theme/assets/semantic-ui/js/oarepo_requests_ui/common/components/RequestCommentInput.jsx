import React, { useState } from "react";
import { RichEditor } from "react-invenio-forms";
import sanitizeHtml from "sanitize-html";
import PropTypes from "prop-types";
import { useQuery } from "@tanstack/react-query";
import { httpApplicationJson } from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Message, Icon } from "semantic-ui-react";

export const RequestCommentInput = ({
  comment,
  handleChange,
  initialValue,
  maxCommentLength,
}) => {
  // when focused move the cursor at the end of any existing content
  const handleFocus = (event, editor) => {
    editor.selection.select(editor.getBody(), true);
    editor.selection.collapse(false);
  };
  let timeoutId;
  const [pasteError, setPasteError] = useState(false);
  const [length, setLength] = useState(initialValue?.length);
  // TODO: there is no appropriate URL to call here. I think this one is the safest, because we know it exists and it does
  // not rely on external library (like those that contain /me that are from dashboard). To be discussed how to handle this appropriately.
  // maybe some link that lives in oarepo ui and that can universaly provide allowed tags and attributes
  const { data } = useQuery(
    ["allowedHtmlTagsAttrs"],
    () => httpApplicationJson.get(`/requests/configs/publish_draft`),
    {
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    }
  );

  const allowedHtmlAttrs = data?.data?.allowedHtmlAttrs;
  const allowedHtmlTags = data?.data?.allowedHtmlTags;

  return (
    <React.Fragment>
      <RichEditor
        initialValue={initialValue}
        inputValue={comment}
        editorConfig={{
          auto_focus: true,
          min_height: 100,
          width: "100%",
          toolbar:
            "blocks | bold italic | bullist numlist | outdent indent | undo redo",
          setup: (editor) => {
            editor.on("BeforeAddUndo", (event) => {
              const length = editor.getContent({ format: "text" }).length;
              if (length >= maxCommentLength) {
                event.preventDefault();
              }
            });
            editor.on("PastePreProcess", (event) => {
              const pastedText = event.content;
              const sanitizedText = sanitizeHtml(pastedText, {
                allowedTags: allowedHtmlTags,
                allowedAttributes: allowedHtmlAttrs,
              });
              const currentCommentLength = editor.getContent({
                format: "text",
              }).length;
              if (
                sanitizedText.length + currentCommentLength >
                maxCommentLength
              ) {
                event.content = sanitizedText.slice(
                  0,
                  maxCommentLength - currentCommentLength
                );
                setPasteError(true);
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => setPasteError(false), 3000);
              }
            });
            editor.on("init", () => {
              setLength(editor.getContent({ format: "text" }).length);
            });
          },
        }}
        onEditorChange={(event, editor) => {
          const cleanedContent = sanitizeHtml(editor.getContent(), {
            allowedTags: allowedHtmlTags,
            allowedAttributes: allowedHtmlAttrs,
          });
          const textContent = editor.getContent({ format: "text" });
          const textLength = textContent.length;

          if (textLength <= maxCommentLength) {
            handleChange(event, cleanedContent);
          }
          // querky  behavior of the editor, when the content is empty, the length is 1
          if (textContent.trim().length === 0) {
            setLength(0);
          } else {
            setLength(textLength);
          }
        }}
        onFocus={handleFocus}
      />
      <small>{`${i18next.t("Remaining characters: ")}${
        maxCommentLength - length
      }`}</small>
      {pasteError && (
        <Message size="mini">
          <Message.Content>
            <Icon name="warning circle" />
            {i18next.t("Pasted text was shortened to fit the allowed length.")}
          </Message.Content>
        </Message>
      )}
    </React.Fragment>
  );
};

RequestCommentInput.propTypes = {
  comment: PropTypes.string,
  handleChange: PropTypes.func,
  initialValue: PropTypes.string,
  maxCommentLength: PropTypes.number,
};

RequestCommentInput.defaultProps = {
  initialValue: "",
  maxCommentLength: 1000,
};
