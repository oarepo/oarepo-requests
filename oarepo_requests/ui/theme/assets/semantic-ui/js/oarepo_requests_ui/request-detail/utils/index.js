import _has from "lodash/has";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import * as Yup from 'yup';

export const hasAll = (obj, ...keys) => keys.every(key => _has(obj, key));

export const hasAny = (obj, ...keys) => keys.some(key => _has(obj, key));

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
