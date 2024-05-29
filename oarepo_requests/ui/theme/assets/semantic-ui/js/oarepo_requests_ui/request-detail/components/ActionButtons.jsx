import React from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Grid, List, Form, Divider, Comment, Header, Container, Icon } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import _sortBy from "lodash/sortBy";
import _has from "lodash/has";
import axios from "axios";

// import { isDeepEmpty } from "@js/oarepo_requests/utils";
import { ConfirmModal } from ".";

const callApi = async (url, method = "GET", data = null) => {
  if (_isEmpty(url)) {
    console.log("URL parameter is missing or invalid.");
  }
  data = { data: data };
  if (_isEmpty(data.data?.payload?.content)) {
    data = null;
  }
  return axios({
    url: url,
    method: method,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/vnd.inveniordm.v1+json'
    },
    ...data
})};

export const ActionButtons = ({ request }) => {
  return (
    <>
      {request.links?.actions?.accept && 
        <ConfirmModal request={request} requestModalHeader={i18next.t("Accept") + " " + i18next.t("request")} 
          handleSubmit={(values) => callApi(request.links.actions.accept, "POST", values)}
          triggerButton={
            <Button positive compact icon="check" content={i18next.t("Accept")} />
          }
        />
      }
      {request.links?.actions?.cancel && 
        <ConfirmModal request={request} requestModalHeader={i18next.t("Cancel") + " " + i18next.t("request")} 
          handleSubmit={(values) => callApi(request.links.actions.cancel, "POST", values)}
          triggerButton={
            <Button compact icon="close" content={i18next.t("Cancel")} />
          }
          submitButton={
            <Button type="submit" form="submit-request-form" negative compact icon="close" content={i18next.t("Cancel") + " " + i18next.t("request")} />
          }
        />
      }
      {request.links?.actions?.decline && 
        <ConfirmModal request={request} requestModalHeader={i18next.t("Decline") + " " + i18next.t("request")} 
          handleSubmit={(values) => callApi(request.links.actions.decline, "POST", values)}
          triggerButton={
            <Button negative compact icon="close" content={i18next.t("Decline")} />
          }
        />
      }
    </>
  );
}