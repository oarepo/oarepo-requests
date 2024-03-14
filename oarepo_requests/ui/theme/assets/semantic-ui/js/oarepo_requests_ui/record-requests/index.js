import React from "react";
import ReactDOM from "react-dom";

import { RecordRequests } from "./components";

// import dummyRecord from "./dummy-record.js";

const recordRequestsAppDiv = document.getElementById("record-requests");

let record = JSON.parse(recordRequestsAppDiv.dataset.record);

console.log(record);

ReactDOM.render(
  <RecordRequests
    record={record}
  />,
  recordRequestsAppDiv
);
