import React from "react";
import ReactDOM from "react-dom";

const recordRequestsAppDiv = document.getElementById("request-detail");

let request = JSON.parse(recordRequestsAppDiv.dataset?.request);

ReactDOM.render(
  <div>Hello World!</div>,
  recordRequestsAppDiv
);