import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";
import { REQUEST_TYPE } from "../../utils/objects";
import { useRequestsApi } from "../../utils/hooks";
import PropTypes from "prop-types";
import { useFormikContext } from "formik";
import { useConfirmModalContext, useModalControlContext } from "../../contexts";

const Accept = ({ request }) => {
  const formik = useFormikContext();
  const { confirmAction } = useConfirmModalContext();
  const modalControl = useModalControlContext();

  const { doAction } = useRequestsApi(
    request,
    formik,
    confirmAction,
    modalControl
  );

  return (
    <Button
      title={i18next.t("Accept request")}
      onClick={() => doAction(REQUEST_TYPE.ACCEPT, true)}
      className="requests request-accept-button"
      positive
      icon
      labelPosition="left"
      floated="right"
    >
      <Icon name="check" />
      {i18next.t("Accept")}
    </Button>
  );
};

Accept.propTypes = {
  request: PropTypes.object,
};

export default Accept;
