import React from "react";

import _isEmpty from "lodash/isEmpty";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";

import { REQUEST_TYPE } from "../../utils/objects";
import { useRequestsApi } from "../../utils/hooks";

const SubmitEvent = ({
  request: eventType,
  requestType,
  onSubmit,
  ...props
}) => {
  const { doAction } = useRequestsApi(eventType, onSubmit);

  return (
    <Button
      title={i18next.t("Submit event")}
      color="blue"
      icon
      labelPosition="left"
      floated="right"
      onClick={() => doAction(REQUEST_TYPE.CREATE)}
      {...props}
    >
      <Icon name="plus" />
      {i18next.t("Submit")}
    </Button>
  );
};

export default SubmitEvent;
