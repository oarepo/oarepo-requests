import React from "react";

import _isEmpty from "lodash/isEmpty";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";

import { REQUEST_TYPE } from "../../utils/objects";
import { useRequestsApi } from "../../utils/hooks";

const Submit = ({ request, requestType, onSubmit, ...props }) => {
  const { doAction } = useRequestsApi(request, onSubmit);

  return (
    <Button
      title={i18next.t("Submit request")}
      color="blue"
      icon
      labelPosition="left"
      floated="right"
      {...props}
      onClick={() => doAction(REQUEST_TYPE.SUBMIT)}
    >
      <Icon name="paper plane" />
      {i18next.t("Submit")}
    </Button>
  );
};

export default Submit;
