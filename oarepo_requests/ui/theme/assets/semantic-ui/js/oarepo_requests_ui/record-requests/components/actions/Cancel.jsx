import React from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";

import { REQUEST_TYPE } from "../../utils/objects";
import { useRequestsApi } from "../../utils/hooks";

const Cancel = ({ request, requestType, onSubmit, ...props }) => {
  const { doAction } = useRequestsApi(request, onSubmit);

  return (
    <Button title={i18next.t("Cancel request")} onClick={() => doAction(REQUEST_TYPE.CANCEL, true)} color="grey" icon labelPosition="left" floated="left" {...props}>
      <Icon name="trash alternate" />
      {i18next.t("Cancel request")}
    </Button>
  );
};

export default Cancel;