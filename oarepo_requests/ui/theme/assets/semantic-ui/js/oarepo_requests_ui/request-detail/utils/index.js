import _has from "lodash/has";
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
