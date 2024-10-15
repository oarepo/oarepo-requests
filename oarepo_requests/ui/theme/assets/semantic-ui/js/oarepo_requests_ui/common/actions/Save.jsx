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
} from "@js/oarepo_requests_common";

const Save = ({ request, requestType, isMutating }) => {
  const formik = useFormikContext();
  const { confirmAction } = useConfirmModalContext();
  const modalControl = useModalControlContext();

  const { isLoading, mutate: createOrSaveRequest } = useAction({
    action: createOrSave,
    requestOrRequestType: request || requestType,
    formik,
    confirmAction,
    modalControl,
  });

  return (
    <Button
      title={i18next.t("Save drafted request")}
      onClick={() => createOrSaveRequest()}
      className="requests request-save-button"
      color="grey"
      icon
      labelPosition="left"
      floated="right"
      loading={isLoading}
      disabled={isMutating > 0}
    >
      <Icon name="save" />
      {i18next.t("Save")}
    </Button>
  );
};

Save.propTypes = {
  request: PropTypes.object,
  requestType: PropTypes.object,
  isMutating: PropTypes.number,
};

export default Save;
