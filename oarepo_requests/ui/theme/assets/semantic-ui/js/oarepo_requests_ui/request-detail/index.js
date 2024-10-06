import React from "react";
import ReactDOM from "react-dom";
import { FormConfigProvider } from "@js/oarepo_ui";
import { RequestDetail } from "./components";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const recordRequestsAppDiv = document.getElementById("request-detail");

let request = recordRequestsAppDiv.dataset?.request
  ? JSON.parse(recordRequestsAppDiv.dataset.request)
  : {};
const formConfig = recordRequestsAppDiv.dataset?.formConfig
  ? JSON.parse(recordRequestsAppDiv.dataset.formConfig)
  : {};
const queryClient = new QueryClient();

ReactDOM.render(
  <FormConfigProvider value={{ formConfig }}>
    <QueryClientProvider client={queryClient}>
      <RequestDetail request={request} />
    </QueryClientProvider>
  </FormConfigProvider>,
  recordRequestsAppDiv
);
