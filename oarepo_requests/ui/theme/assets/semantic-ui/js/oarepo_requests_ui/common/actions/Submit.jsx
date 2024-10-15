import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";
import { useFormikContext } from "formik";
import {
  useConfirmModalContext,
  useModalControlContext,
  useAction,
  saveAndSubmit,
  REQUEST_TYPE,
} from "@js/oarepo_requests_common";

const Submit = ({ request, extraData, isMutating }) => {
  const formik = useFormikContext();
  const { confirmAction } = useConfirmModalContext();
  const modalControl = useModalControlContext();

  const { isLoading, mutate: saveAndSubmitRequest } = useAction({
    action: saveAndSubmit,
    requestOrRequestType: request,
    formik,
    confirmAction,
    modalControl,
  });
  const requireConfirmation = extraData?.hasForm || extraData?.dangerous;

  const handleClick = () => {
    if (requireConfirmation) {
      confirmAction(
        () => saveAndSubmitRequest(),
        REQUEST_TYPE.SUBMIT,
        extraData
      );
    } else {
      saveAndSubmitRequest();
    }
  };

  return (
    <Button
      title={i18next.t("Submit request")}
      color="blue"
      className="requests request-submit-button"
      icon
      labelPosition="left"
      floated="right"
      onClick={() => handleClick()}
      loading={isLoading}
      disabled={isMutating > 0}
    >
      <Icon name="paper plane" />
      {i18next.t("Submit")}
    </Button>
  );
};

Submit.propTypes = {
  request: PropTypes.object,
  extraData: PropTypes.object,
  isMutating: PropTypes.number,
};

export default Submit;
