import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";
import { useRequestsApi } from "../../utils/hooks";
import { REQUEST_TYPE } from "../../utils/objects";
import PropTypes from "prop-types";
import { useFormikContext } from "formik";
import { useConfirmModalContext, useModalControlContext } from "../../contexts";
const Create = ({ requestType }) => {
  const formik = useFormikContext();
  const { confirmAction } = useConfirmModalContext();
  const modalControl = useModalControlContext();

  const { doAction } = useRequestsApi(
    requestType,
    formik,
    confirmAction,
    modalControl
  );

  return (
    <Button
      type="submit"
      form="request-form"
      name="create-request"
      className="requests request-create-button"
      title={i18next.t("Create request")}
      color="blue"
      icon
      labelPosition="left"
      floated="right"
      onClick={() => doAction(REQUEST_TYPE.CREATE)}
    >
      <Icon name="plus" />
      {i18next.t("Create")}
    </Button>
  );
};

Create.propTypes = {
  requestType: PropTypes.object,
};

export default Create;
