import React from "react";
import ReactDOM from "react-dom";

import { FormConfigProvider} from "@js/oarepo_ui";
import { RequestDetail } from "./components";

const recordRequestsAppDiv = document.getElementById("request-detail");

let request = recordRequestsAppDiv.dataset?.request ? JSON.parse(recordRequestsAppDiv.dataset.request) : {};
const formConfig = recordRequestsAppDiv.dataset?.formConfig ? JSON.parse(recordRequestsAppDiv.dataset.formConfig) : {};

ReactDOM.render(
    <FormConfigProvider value={{formConfig}}>
        <RequestDetail request={request} />
    </FormConfigProvider>,
  recordRequestsAppDiv
);
