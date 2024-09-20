import React from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";
import { useRequestsApi } from "../../utils/hooks";
import { REQUEST_TYPE } from "../../utils/objects";

const Create = ({ request, requestType, onSubmit, ...props }) => {
  const { doAction } = useRequestsApi(requestType, onSubmit);

  return (
    <Button
      type="submit"
      form="request-form"
      name="create-request"
      title={i18next.t("Create request")}
      color="blue"
      icon
      labelPosition="left"
      floated="right"
      onClick={() => doAction(REQUEST_TYPE.CREATE)}
      {...props}
    >
      <Icon name="plus" />
      {i18next.t("Create")}
    </Button>
  );
};

export default Create;
