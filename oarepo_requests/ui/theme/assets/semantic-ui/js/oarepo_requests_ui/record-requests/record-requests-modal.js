import React from "react";
import ReactDOM from "react-dom";
import { RecordRequestsListModal } from "@js/oarepo_requests_common/";
const recordRequestsModal = document.getElementById("record-requests-modal");
if (recordRequestsModal) {
  ReactDOM.render(
    <RecordRequestsListModal
      endpointUrl={
        JSON.parse(recordRequestsModal.dataset.record)?.links?.requests
      }
    />,
    recordRequestsModal
  );
}
