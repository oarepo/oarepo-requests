import React from "react";

import _isEmpty from "lodash/isEmpty";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";

import { REQUEST_TYPE } from "../../utils/objects";
import { useRequestsApi } from "../../utils/hooks";

const SubmitEvent = ({ request: eventType, requestType, onSubmit, ...props }) => {
  const { doAction } = useRequestsApi(eventType, onSubmit);
  
  const formWillBeRendered = !_isEmpty(eventType?.payload_ui);
  let extraProps;
  if (formWillBeRendered) {
    extraProps = { type: "submit", form: "request-form", name: "submit-event" };
  } else {
    extraProps = { onClick: () => doAction(REQUEST_TYPE.CREATE) };
  }

  return (
    <Button
      title={i18next.t("Submit event")} color="blue" icon labelPosition="left" floated="right"
      {...extraProps}
      {...props}
    >
      <Icon name="plus" />
      {i18next.t("Submit")}
    </Button>
  );
}

export default SubmitEvent;