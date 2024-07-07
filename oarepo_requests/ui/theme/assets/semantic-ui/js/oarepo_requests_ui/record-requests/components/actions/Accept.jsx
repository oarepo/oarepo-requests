import React from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";

import { REQUEST_TYPE } from "../../utils/objects";
import { useRequestsApi } from "../../utils/hooks";

const Accept = ({ request, onSubmit, ...props }) => {
  const { doAction } = useRequestsApi(request, onSubmit);
  
  return (
    <Button title={i18next.t("Accept request")} onClick={() => doAction(REQUEST_TYPE.ACCEPT, true)} positive icon labelPosition="left" floated="right" {...props}>
      <Icon name="check" />
      {i18next.t("Accept")}
    </Button>
  );
}

export default Accept;