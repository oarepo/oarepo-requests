import React from "react";
import ReactDOM from "react-dom";

import _isEmpty from "lodash/isEmpty";

import { RecordRequests } from "./components";

const recordRequestsAppDiv = document.getElementById("record-requests");

let record = JSON.parse(recordRequestsAppDiv.dataset.record);

if (!_isEmpty(record?.request_types) || !_isEmpty(record?.requests)) {
  ReactDOM.render(
    <RecordRequests
      record={record}
    />,
    recordRequestsAppDiv
  );
}