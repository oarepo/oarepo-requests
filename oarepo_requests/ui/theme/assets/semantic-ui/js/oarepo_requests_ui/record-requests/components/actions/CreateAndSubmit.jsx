import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";

import { useRequestsApi } from "../../utils/hooks";

const CreateAndSubmit = ({ requestType, onSubmit, ...props }) => {
  const { doCreateAndSubmitAction } = useRequestsApi(requestType, onSubmit);

  return (
    <Button
      title={i18next.t("Submit request")}
      color="blue"
      icon
      labelPosition="left"
      floated="right"
      {...props}
      onClick={() => doCreateAndSubmitAction()}
    >
      <Icon name="paper plane" />
      {i18next.t("Submit")}
    </Button>
  );
};

export default CreateAndSubmit;
