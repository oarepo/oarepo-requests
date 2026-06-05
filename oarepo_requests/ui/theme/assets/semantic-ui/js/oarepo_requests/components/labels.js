// Copyright (c) 2024 CESNET
// SPDX-License-Identifier: MIT

import { i18next } from "@translations/invenio_requests/i18next";
import React from "react";
import { Label } from "semantic-ui-react";

const makeTypeLabel = (text) =>
  function TypeLabel() {
    return (
      <Label horizontal className="primary theme-secondary" size="small">
        {i18next.t(text)}
      </Label>
    );
  };

export const LabelTypePublishDraft = makeTypeLabel("Publish draft");
export const LabelTypeNewVersion = makeTypeLabel("New version");
export const LabelTypePublishNewVersion = makeTypeLabel("Publish new version");
export const LabelTypePublishChangedMetadata = makeTypeLabel(
  "Publish changed metadata"
);
export const LabelTypeDeletePublishedRecord = makeTypeLabel("Record deletion");
export const LabelTypeEditPublishedRecord = makeTypeLabel("Edit published record");
