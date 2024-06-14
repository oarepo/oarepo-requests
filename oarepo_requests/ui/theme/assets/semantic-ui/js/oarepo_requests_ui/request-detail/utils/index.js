import _has from "lodash/has";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import * as Yup from 'yup';
import sanitizeHtml from "sanitize-html";
import { decode } from "html-entities";

const ALLOWED_HTML_TAGS = [
    "a",
    "abbr",
    "acronym",
    "b",
    "blockquote",
    "br",
    "code",
    "div",
    "table",
    "tbody",
    "td",
    "th",
    "tr",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "i",
    "li",
    "ol",
    "p",
    "pre",
    "span",
    "strike",
    "strong",
    "sub",
    "sup",
    "u",
    "ul",
]


const ALLOWED_HTML_ATTRS = {
    "a": ["href", "title", "name", "target", "rel"],
    "abbr": ["title"],
    "acronym": ["title"],
}

export const hasAll = (obj, ...keys) => keys.every(key => _has(obj, key));
export const hasAny = (obj, ...keys) => keys.some(key => _has(obj, key));

export const sanitizeInput = (htmlString, validTags) => {
  const decodedString = decode(htmlString);
  const cleanInput = sanitizeHtml(decodedString, {
    allowedTags: validTags || ALLOWED_HTML_TAGS,
    allowedAttributes: ALLOWED_HTML_ATTRS,
  });
  return cleanInput;
};

export const CommentPayloadSchema = Yup.object().shape({
  payload: Yup.object().shape({
    content: Yup.string()
      .min(1, i18next.t("Comment must be at least 1 character long."))
      .required(i18next.t("Comment must be at least 1 character long.")),
    format: Yup.string().equals(["html"], i18next.t("Invalid format."))
  })
});

export const getRequestStatusIcon = (requestStatus) => { 
  switch (requestStatus?.toLowerCase()) {
    case "created":
      return { name: "clock outline", color: "grey" };
    case "submitted":
      return { name: "clock", color: "grey" };
    case "cancelled":
      return { name: "square", color: "black" };
    case "accepted":
      return { name: "check circle", color: "green" };
    case "declined":
      return { name: "close", color: "red" };
    case "expired":
      return { name: "hourglass end", color: "orange" };
    case "deleted":
      return { name: "thrash", color: "black" };
    default:
      return null;
  }
};
