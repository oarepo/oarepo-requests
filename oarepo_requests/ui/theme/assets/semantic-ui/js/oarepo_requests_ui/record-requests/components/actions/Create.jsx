import React from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";

const Create = ({ ...props }) => {
  return (
    <Button type="submit" form="request-form" name="create-request" title={i18next.t("Create request")} color="blue" icon labelPosition="left" floated="right" {...props}>
      <Icon name="plus" />
      {i18next.t("Create")}
    </Button>
  );
}

export default Create;