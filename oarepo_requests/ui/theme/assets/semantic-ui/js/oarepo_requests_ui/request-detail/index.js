// This file is part of InvenioRequests
// Copyright (C) 2022-2024 CERN.
// Copyright (C) 2024 Northwestern University.
// Copyright (C) 2024 KTH Royal Institute of Technology.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import ReactDOM from "react-dom";
import { overrideStore } from "react-overridable";
import { InvenioRequestsApp } from "@js/invenio_requests/InvenioRequestsApp";
import defaultOverrides from "@js/oarepo_requests_common/defaultOverrides";
import { FormikRefContextProvider, CallbackContextProvider } from "../common";
import { RequestActionsPortal } from "./RequestActionsPortal";
import { RequestDetails } from "../common/RequestDetail";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient();

const requestDetailsDiv = document.getElementById("request-detail");
const request = JSON.parse(requestDetailsDiv.dataset.record);
const defaultQueryParams = JSON.parse(
  requestDetailsDiv.dataset.defaultQueryConfig
);
// const defaultReplyQueryParams = JSON.parse(
//   requestDetailsDiv.dataset.defaultReplyQueryConfig
// );
const userAvatar = JSON.parse(requestDetailsDiv.dataset.userAvatar);
const permissions = JSON.parse(requestDetailsDiv.dataset.permissions);
const config = JSON.parse(requestDetailsDiv.dataset.config);
const overriddenComponents = overrideStore.getAll();

const defaultComponents = {
  ...defaultOverrides,
  ...{
    "InvenioRequests.RequestActionsPortal": RequestActionsPortal,
    "InvenioRequests.RequestDetails.layout": RequestDetails,
  },
  ...overriddenComponents,
};

ReactDOM.render(
  <FormikRefContextProvider>
    <QueryClientProvider client={queryClient}>
      <InvenioRequestsApp
        request={request}
        defaultQueryParams={defaultQueryParams}
        // defaultReplyQueryParams={defaultReplyQueryParams}
        overriddenCmps={defaultComponents}
        userAvatar={userAvatar}
        permissions={permissions}
        config={config}
      />
    </QueryClientProvider>
  </FormikRefContextProvider>,
  requestDetailsDiv
);
