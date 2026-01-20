import { i18next } from "@translations/oarepo_requests_ui/i18next";
import React, { useEffect } from "react";
import { Button } from "semantic-ui-react";
import PropTypes from "prop-types";
import { useRequestActionContext } from "../contexts";

export const RequestSubmitButton = ({
  onClick,
  loading,
  ariaAttributes,
  size,
  content,
  className,
}) => {
  const { request } = useRequestActionContext();
  return (
    <Button
      icon="send"
      labelPosition="left"
      content={i18next.t("Submit request")}
      onClick={onClick}
      positive
      loading={loading}
      disabled={loading}
      size={size}
      className={className}
      {...ariaAttributes}
    />
  );
};

RequestSubmitButton.propTypes = {
  onClick: PropTypes.func.isRequired,
  loading: PropTypes.bool,
  ariaAttributes: PropTypes.object,
  size: PropTypes.string,
  content: PropTypes.string,
  className: PropTypes.string,
};
