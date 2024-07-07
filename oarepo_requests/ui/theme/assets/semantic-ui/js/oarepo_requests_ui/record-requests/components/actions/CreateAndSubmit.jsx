import React from "react";

import _isEmpty from "lodash/isEmpty";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";

import { useRequestsApi } from "../../utils/hooks";

const CreateAndSubmit = ({ request, requestType, onSubmit, ...props }) => {
  const { doCreateAndSubmitAction } = useRequestsApi(request, onSubmit);
  
  const formWillBeRendered = !_isEmpty(requestType?.payload_ui);
  let extraProps;
  if (formWillBeRendered) {
    extraProps = { type: "submit", form: "request-form", name: "create-and-submit-request" };
  } else {
    extraProps = { onClick: () => doCreateAndSubmitAction() };
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

export default CreateAndSubmit;