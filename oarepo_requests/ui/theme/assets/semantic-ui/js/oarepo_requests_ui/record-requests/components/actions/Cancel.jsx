import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";
import { REQUEST_TYPE } from "../../utils/objects";
import { useRequestsApi } from "../../utils/hooks";
import PropTypes from "prop-types";

const Cancel = ({ request }) => {
  const { doAction } = useRequestsApi(request);

  return (
    <Button
      title={i18next.t("Cancel request")}
      onClick={() => doAction(REQUEST_TYPE.CANCEL, true)}
      className="requests request-cancel-button"
      color="grey"
      icon
      labelPosition="left"
      floated="left"
    >
      <Icon name="trash alternate" />
      {i18next.t("Cancel request")}
    </Button>
  );
};

Cancel.propTypes = {
  request: PropTypes.object,
};

export default Cancel;
