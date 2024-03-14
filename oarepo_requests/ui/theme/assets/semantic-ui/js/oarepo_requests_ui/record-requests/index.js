import React from "react";
import ReactDOM from "react-dom";

import { RecordRequests } from "./components";

const recordRequestsAppDiv = document.getElementById("record-requests");

let record = JSON.parse(recordRequestsAppDiv.dataset.record);

ReactDOM.render(
  <RecordRequests
    record={record}
  />,
  recordRequestsAppDiv
);
