import React from "react";
import ReactDOM from "react-dom";
import { RecordRequestsListModal } from "@js/oarepo_requests_common/";
const recordRequestsModal = document.getElementById("record-requests-modal");
if (recordRequestsModal) {
  const record = JSON.parse(recordRequestsModal.dataset.record);
  ReactDOM.render(
    <RecordRequestsListModal
      endpointUrl={record?.links?.requests}
      recordTitle={record?.metadata?.title}
    />,
    recordRequestsModal
  );
}
