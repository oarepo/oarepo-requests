import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";
import { useFormikContext } from "formik";
import {
  useConfirmModalContext,
  useModalControlContext,
  useAction,
  cancel,
  REQUEST_TYPE,
} from "@js/oarepo_requests_common";

const Cancel = ({ request, extraData }) => {
  const formik = useFormikContext();
  const { confirmAction } = useConfirmModalContext();
  const modalControl = useModalControlContext();
  const requireConfirmation = extraData?.hasForm || extraData?.dangerous;

  const { isLoading, mutate: cancelRequest } = useAction({
    action: cancel,
    requestOrRequestType: request,
    formik,
    confirmAction,
    modalControl,
  });

  const handleClick = () => {
    if (requireConfirmation) {
      confirmAction(() => cancelRequest(), REQUEST_TYPE.CANCEL, extraData);
    } else {
      cancelRequest();
    }
  };

  return (
    <Button
      title={i18next.t("Cancel request")}
      onClick={() => handleClick()}
      className="requests request-cancel-button"
      color="grey"
      icon
      labelPosition="left"
      floated="left"
      loading={isLoading}
      disabled={isLoading}
    >
      <Icon name="trash alternate" />
      {i18next.t("Cancel request")}
    </Button>
  );
};

Cancel.propTypes = {
  request: PropTypes.object,
  extraData: PropTypes.object,
};

export default Cancel;
