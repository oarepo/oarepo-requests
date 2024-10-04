import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";
import { useFormikContext } from "formik";
import {
  useConfirmModalContext,
  useModalControlContext,
  REQUEST_TYPE,
  useRequestsApi,
} from "@js/oarepo_requests_common";

const Decline = ({ request }) => {
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
      title={i18next.t("Decline request")}
      onClick={() => doAction(REQUEST_TYPE.DECLINE, true)}
      negative
      className="requests request-decline-button"
      icon
      labelPosition="left"
      floated="left"
    >
      <Icon name="cancel" />
      {i18next.t("Decline")}
    </Button>
  );
};

Decline.propTypes = {
  request: PropTypes.object,
};

export default Decline;
