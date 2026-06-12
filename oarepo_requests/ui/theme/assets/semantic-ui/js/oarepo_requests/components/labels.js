// Copyright (c) 2024 CESNET
// SPDX-License-Identifier: MIT

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import React from "react";
import { Label } from "semantic-ui-react";

// using plain functions, so that string extraction would work correctly with i18next-scanner
export const LabelTypePublishDraft = () => (
  <Label horizontal className="primary theme-secondary" size="small">
    {i18next.t("Publish draft")}
  </Label>
);

export const LabelTypeNewVersion = () => (
  <Label horizontal className="primary theme-secondary" size="small">
    {i18next.t("New version")}
  </Label>
);

export const LabelTypePublishNewVersion = () => (
  <Label horizontal className="primary theme-secondary" size="small">
    {i18next.t("Publish new version")}
  </Label>
);

export const LabelTypePublishChangedMetadata = () => (
  <Label horizontal className="primary theme-secondary" size="small">
    {i18next.t("Publish changed metadata")}
  </Label>
);

export const LabelTypeDeletePublishedRecord = () => (
  <Label horizontal className="primary theme-secondary" size="small">
    {i18next.t("Record deletion")}
  </Label>
);

export const LabelTypeEditPublishedRecord = () => (
  <Label horizontal className="primary theme-secondary" size="small">
    {i18next.t("Edit published record")}
  </Label>
);
