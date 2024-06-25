import React from "react";
import ReactDOM from "react-dom";

import { RequestDetail } from "./components";

const recordRequestsAppDiv = document.getElementById("request-detail");

let request = recordRequestsAppDiv.dataset?.request ? JSON.parse(recordRequestsAppDiv.dataset.request) : {};

ReactDOM.render(
  <RequestDetail request={request} />,
  recordRequestsAppDiv
);
