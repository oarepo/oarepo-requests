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

const Cancel = ({ request }) => {
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
