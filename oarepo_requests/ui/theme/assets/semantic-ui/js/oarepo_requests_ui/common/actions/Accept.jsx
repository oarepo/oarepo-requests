import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";
import { useFormikContext } from "formik";
import {
  useConfirmModalContext,
  useModalControlContext,
  useAction,
  accept,
  REQUEST_TYPE,
} from "@js/oarepo_requests_common";

const Accept = ({ request, extraData }) => {
  const formik = useFormikContext();
  const { confirmAction } = useConfirmModalContext();
  const modalControl = useModalControlContext();
  const requireConfirmation = extraData?.hasForm || extraData?.dangerous;

  const { isLoading, mutate: acceptRequest } = useAction({
    action: accept,
    requestOrRequestType: request,
    formik,
    confirmAction,
    modalControl,
  });

  const handleClick = () => {
    if (requireConfirmation) {
      confirmAction(() => acceptRequest(), REQUEST_TYPE.ACCEPT, extraData);
    } else {
      acceptRequest();
    }
  };

  return (
    <Button
      title={i18next.t("Accept request")}
      onClick={() => handleClick()}
      className="requests request-accept-button"
      positive
      icon
      labelPosition="left"
      floated="right"
      loading={isLoading}
      disabled={isLoading}
    >
      <Icon name="check" />
      {i18next.t("Accept")}
    </Button>
  );
};

Accept.propTypes = {
  request: PropTypes.object,
  extraData: PropTypes.object,
};

export default Accept;
