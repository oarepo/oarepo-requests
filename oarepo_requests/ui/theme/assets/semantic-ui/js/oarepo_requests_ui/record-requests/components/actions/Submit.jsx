import React from "react";

import _isEmpty from "lodash/isEmpty";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";

import { REQUEST_TYPE } from "../../utils/objects";
import { useRequestsApi } from "../../utils/hooks";

const Submit = ({ request, requestType, onSubmit, ...props }) => {
  const { doAction } = useRequestsApi(request, onSubmit);
  
  const formWillBeRendered = !_isEmpty(requestType?.payload_ui);
  let extraProps;
  if (formWillBeRendered) {
    extraProps = { type: "submit", form: "request-form", name: "submit-request" };
  } else {
    extraProps = { onClick: () => doAction(REQUEST_TYPE.SUBMIT) };
  }

  return (
    <Button
      title={i18next.t("Submit request")} color="blue" icon labelPosition="left" floated="right"
      {...extraProps}
      {...props}
    >
      <Icon name="paper plane" />
      {i18next.t("Submit")}
    </Button>
  );
}

export default Submit;