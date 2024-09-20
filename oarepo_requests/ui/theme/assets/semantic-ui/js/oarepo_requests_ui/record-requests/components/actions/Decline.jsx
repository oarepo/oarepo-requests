import React from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";

import { REQUEST_TYPE } from "../../utils/objects";
import { useRequestsApi } from "../../utils/hooks";

const Decline = ({ request, onSubmit, ...props }) => {
  const { doAction } = useRequestsApi(request, onSubmit);

  return (
    <Button
      title={i18next.t("Decline request")}
      onClick={() => doAction(REQUEST_TYPE.DECLINE, true)}
      negative
      icon
      labelPosition="left"
      floated="left"
      {...props}
    >
      <Icon name="cancel" />
      {i18next.t("Decline")}
    </Button>
  );
};

export default Decline;
