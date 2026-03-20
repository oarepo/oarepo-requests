/*
 * Copyright (C) 2024 CESNET z.s.p.o.
 *
 * oarepo-requests is free software; you can redistribute it and/or
 * modify it under the terms of the MIT License; see LICENSE file for more
 * details.
 */
import _isArray from "lodash/isArray";
import _isObjectLike from "lodash/isObject";
import _every from "lodash/every";
import _isString from "lodash/isString";
import { i18next } from "@translations/oarepo_requests_ui/i18next";

export const getRequestStatusIcon = (requestStatus) => {
  switch (requestStatus?.toLowerCase()) {
    case "created":
      return { name: "clock outline", color: "grey" };
    case "submitted":
      return { name: "clock", color: "grey" };
    case "cancelled":
      return { name: "ban", color: "black" };
    case "accepted":
      return { name: "check circle", color: "green" };
    case "declined":
      return { name: "close", color: "red" };
    case "expired":
      return { name: "hourglass end", color: "orange" };
    case "deleted":
      return { name: "trash", color: "black" };
    case "comment_deleted":
      return { name: "eraser", color: "grey" };
    case "edited":
      return { name: "pencil", color: "grey" };
    default:
      return null;
  }
};

export const getFeedMessage = (eventStatus) => {
  switch (eventStatus?.toLowerCase()) {
    case "created":
      return i18next.t("requestCreated");
    case "submitted":
      return i18next.t("requestSubmitted");
    case "cancelled":
      return i18next.t("requestCancelled");
    case "accepted":
      return i18next.t("requestAccepted");
    case "declined":
      return i18next.t("requestDeclined");
    case "expired":
      return i18next.t("Request expired.");
    case "deleted":
      return i18next.t("requestDeleted");
    case "comment_deleted":
      return i18next.t("deleted comment");
    case "edited":
      return i18next.t("requestEdited");
    default:
      return i18next.t("requestCommented");
  }
};

// Format complex object values for string-like format
export const formatValueToStringLikeFormat = (value) => {
  if (value === null || value === undefined) return "—";
  if (_isArray(value) && _every(value, _isString)) return value.join(", ");
  if (_isObjectLike(value)) return JSON.stringify(value, null, 2);
  return String(value);
};

// Convert (nested) record field path to human readable format
export const formatNestedRecordFieldPath = (path) => {
  return path
    .replace(/^\//, "")
    .replace(/\/(\d+)\//g, (match, arrayIndex) => {
      return ` › ${Number.parseInt(arrayIndex) + 1} › `;
    })
    .replace(/\/(\d+)$/, (match, arrayIndex) => {
      return ` › ${Number.parseInt(arrayIndex) + 1}`;
    })
    .replace(/\//g, " › ");
};
