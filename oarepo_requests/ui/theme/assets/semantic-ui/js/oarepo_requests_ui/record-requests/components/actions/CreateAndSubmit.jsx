import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";
import { useRequestsApi } from "../../utils/hooks";
import PropTypes from "prop-types";
import { useFormikContext } from "formik";
import { useConfirmModalContext, useModalControlContext } from "../../contexts";

const CreateAndSubmit = ({ requestType }) => {
  const formik = useFormikContext();
  const { confirmAction } = useConfirmModalContext();
  const modalControl = useModalControlContext();
  const { doCreateAndSubmitAction } = useRequestsApi(
    requestType,
    formik,
    confirmAction,
    modalControl
  );
  return (
    <Button
      title={i18next.t("Submit request")}
      className="requests request-create-and-submit-button"
      color="blue"
      icon
      labelPosition="left"
      floated="right"
      onClick={() => doCreateAndSubmitAction()}
    >
      <Icon name="paper plane" />
      {i18next.t("Submit")}
    </Button>
  );
};

CreateAndSubmit.propTypes = {
  requestType: PropTypes.object,
};

export default CreateAndSubmit;
