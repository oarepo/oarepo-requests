import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";
import { useFormikContext } from "formik";
import {
  useConfirmModalContext,
  useModalControlContext,
  useAction,
  createOrSave,
  REQUEST_TYPE,
} from "@js/oarepo_requests_common";

const Create = ({ requestType, extraData }) => {
  const formik = useFormikContext();
  const { confirmAction } = useConfirmModalContext();
  const modalControl = useModalControlContext();
  const requireConfirmation = extraData?.hasForm || extraData?.dangerous;

  const { isLoading, mutate: createOrSaveRequest } = useAction({
    action: createOrSave,
    requestOrRequestType: requestType,
    formik,
    confirmAction,
    modalControl,
  });

  const handleClick = () => {
    if (requireConfirmation) {
      confirmAction(
        () => createOrSaveRequest(),
        REQUEST_TYPE.CREATE,
        extraData
      );
    } else {
      createOrSaveRequest();
    }
  };
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
      onClick={() => handleClick()}
      loading={isLoading}
      disabled={isLoading}
    >
      <Icon name="plus" />
      {i18next.t("Create")}
    </Button>
  );
};

Create.propTypes = {
  requestType: PropTypes.object,
  requireConfirmation: PropTypes.bool,
};

export default Create;
