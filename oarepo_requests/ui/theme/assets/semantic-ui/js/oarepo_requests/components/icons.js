// Copyright (c) 2024 CESNET
// SPDX-License-Identifier: MIT

import React from "react";
import { Icon } from "semantic-ui-react";

const makeTypeIcon = (name) =>
  function TypeIcon() {
    return <Icon name={name} className="neutral" />;
  };

export const IconTypePublishDraft = makeTypeIcon("cloud upload");
export const IconTypeNewVersion = makeTypeIcon("code branch");
export const IconTypePublishNewVersion = makeTypeIcon("cloud upload");
export const IconTypePublishChangedMetadata = makeTypeIcon("edit");
export const IconTypeDeletePublishedRecord = makeTypeIcon("trash");
export const IconTypeEditPublishedRecord = makeTypeIcon("edit");
