// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { AppMedia } from "@js/invenio_theme/Media";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import React from "react";
import PropTypes from "prop-types";
import { Dropdown } from "semantic-ui-react";
import { RequestSubmitButton } from "./Buttons";

const { MediaContextProvider, Media } = AppMedia;

export const RequestSubmitModalTrigger = ({
  onClick,
  requestType,
  loading,
  ariaAttributes,
  size,
  className,
}) => {
  const text = i18next.t("Request access");
  return (
    <MediaContextProvider>
      <Media greaterThanOrEqual="tablet">
        <RequestSubmitButton
          onClick={onClick}
          loading={loading}
          disabled={loading}
          requestType={requestType}
          size={size}
          className={className}
          {...ariaAttributes}
        />
      </Media>
      <Media at="mobile">
        <Dropdown.Item
          icon={{
            name: "unlock alternate",
            color: "positive",
            className: "mr-5",
          }}
          onClick={onClick}
          content={text}
        />
      </Media>
    </MediaContextProvider>
  );
};

RequestSubmitModalTrigger.propTypes = {
  onClick: PropTypes.func.isRequired,
  requestType: PropTypes.string.isRequired,
  loading: PropTypes.bool,
  ariaAttributes: PropTypes.object,
  size: PropTypes.string,
  className: PropTypes.string,
};
