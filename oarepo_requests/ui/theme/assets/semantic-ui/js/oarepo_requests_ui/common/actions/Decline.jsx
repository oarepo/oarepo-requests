import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";
import { useFormikContext } from "formik";
import {
  useConfirmModalContext,
  useModalControlContext,
  useAction,
  decline,
  REQUEST_TYPE,
} from "@js/oarepo_requests_common";

const Decline = ({ request, extraData }) => {
  const formik = useFormikContext();
  const { confirmAction } = useConfirmModalContext();
  const modalControl = useModalControlContext();
  const requireConfirmation = extraData?.hasForm || extraData?.dangerous;

  const { isLoading, mutate: declineRequest } = useAction({
    action: decline,
    requestOrRequestType: request,
    formik,
    confirmAction,
    modalControl,
  });

  const handleClick = () => {
    if (requireConfirmation) {
      confirmAction(() => declineRequest(), REQUEST_TYPE.DECLINE, extraData);
    } else {
      declineRequest();
    }
  };

  return (
    <Button
      title={i18next.t("Decline request")}
      onClick={() => handleClick()}
      negative
      className="requests request-decline-button"
      icon
      labelPosition="left"
      floated="left"
      loading={isLoading}
      disabled={isLoading}
    >
      <Icon name="cancel" />
      {i18next.t("Decline")}
    </Button>
  );
};

Decline.propTypes = {
  request: PropTypes.object,
  extraData: PropTypes.object,
};

export default Decline;
