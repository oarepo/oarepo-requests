import React from "react";
import ReactDOM from "react-dom";

import { RecordRequests } from "./components";

const recordRequestsAppDiv = document.getElementById("record-requests");

if (recordRequestsAppDiv) {
  const record = JSON.parse(recordRequestsAppDiv.dataset.record);

  ReactDOM.render(<RecordRequests record={record} />, recordRequestsAppDiv);
}
