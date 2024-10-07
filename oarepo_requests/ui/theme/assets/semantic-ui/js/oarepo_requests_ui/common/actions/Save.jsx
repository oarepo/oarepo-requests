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

const Save = ({ request, extraData }) => {
  const formik = useFormikContext();
  const { confirmAction } = useConfirmModalContext();
  const modalControl = useModalControlContext();

  const { isLoading, mutate: createOrSaveRequest } = useAction({
    action: createOrSave,
    requestOrRequestType: request,
    formik,
    confirmAction,
    modalControl,
  });
  const requireConfirmation = extraData?.hasForm || extraData?.dangerous;

  const handleClick = () => {
    if (requireConfirmation) {
      confirmAction(() => createOrSaveRequest(), REQUEST_TYPE.SAVE, extraData);
    } else {
      createOrSaveRequest();
    }
  };

  return (
    <Button
      title={i18next.t("Save drafted request")}
      onClick={() => handleClick()}
      className="requests request-save-button"
      color="grey"
      icon
      labelPosition="left"
      floated="right"
      loading={isLoading}
      disabled={isLoading}
    >
      <Icon name="save" />
      {i18next.t("Save")}
    </Button>
  );
};

Save.propTypes = {
  request: PropTypes.object,
  requireConfirmation: PropTypes.bool,
};

export default Save;
