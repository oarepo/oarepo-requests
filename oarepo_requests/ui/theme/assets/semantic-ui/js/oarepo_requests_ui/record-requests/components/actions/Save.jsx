import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";
import { REQUEST_TYPE } from "../../utils/objects";
import { useRequestsApi } from "../../utils/hooks";
import PropTypes from "prop-types";

const Save = ({ request }) => {
  const { doAction } = useRequestsApi(request);

  return (
    <Button
      title={i18next.t("Save drafted request")}
      onClick={() => doAction(REQUEST_TYPE.SAVE)}
      className="requests request-save-button"
      color="grey"
      icon
      labelPosition="left"
      floated="right"
    >
      <Icon name="save" />
      {i18next.t("Save")}
    </Button>
  );
};

Save.propTypes = {
  request: PropTypes.object,
};

export default Save;
