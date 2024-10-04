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

const Save = ({ request }) => {
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
