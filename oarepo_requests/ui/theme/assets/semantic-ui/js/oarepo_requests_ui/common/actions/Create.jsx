import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";
import { useFormikContext } from "formik";
import {
  useConfirmModalContext,
  useModalControlContext,
  useRequestsApi,
  REQUEST_TYPE,
} from "@js/oarepo_requests_common";
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
