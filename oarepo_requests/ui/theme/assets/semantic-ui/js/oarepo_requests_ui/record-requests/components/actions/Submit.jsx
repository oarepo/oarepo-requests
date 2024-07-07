import React from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";

const Submit = ({ ...props }) => {
  return (
    <Button type="submit" form="request-form" name="create-and-submit-request" title={i18next.t("Submit request")} color="blue" icon labelPosition="left" floated="right" {...props}>
      <Icon name="paper plane" />
      {i18next.t("Submit")}
    </Button>
  );
}

export default Submit;