import React from "react";
import ReactDOM from "react-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RecordRequests } from "./components";

const queryClient = new QueryClient();

const recordRequestsAppDiv = document.getElementById("record-requests");

if (recordRequestsAppDiv) {
  const record = JSON.parse(recordRequestsAppDiv.dataset.record);

  ReactDOM.render(
    <QueryClientProvider client={queryClient}>
      <RecordRequests record={record} />
    </QueryClientProvider>,
    recordRequestsAppDiv
  );
}
