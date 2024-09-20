import React from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";

import { REQUEST_TYPE } from "../../utils/objects";
import { useRequestsApi } from "../../utils/hooks";

const Save = ({ request, onSubmit, ...props }) => {
  const { doAction } = useRequestsApi(request, onSubmit);

  return (
    <Button
      title={i18next.t("Save drafted request")}
      onClick={() => doAction(REQUEST_TYPE.SAVE)}
      color="grey"
      icon
      labelPosition="left"
      floated="right"
      {...props}
    >
      <Icon name="save" />
      {i18next.t("Save")}
    </Button>
  );
};

export default Save;
