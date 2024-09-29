import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";
import { REQUEST_TYPE } from "../../utils/objects";
import { useRequestsApi } from "../../utils/hooks";
import PropTypes from "prop-types";

const Submit = ({ request }) => {
  const { doAction } = useRequestsApi(request);

  return (
    <Button
      title={i18next.t("Submit request")}
      color="blue"
      className="requests request-submit-button"
      icon
      labelPosition="left"
      floated="right"
      onClick={() => doAction(REQUEST_TYPE.SUBMIT)}
    >
      <Icon name="paper plane" />
      {i18next.t("Submit")}
    </Button>
  );
};

Submit.propTypes = {
  request: PropTypes.object,
};

export default Submit;
