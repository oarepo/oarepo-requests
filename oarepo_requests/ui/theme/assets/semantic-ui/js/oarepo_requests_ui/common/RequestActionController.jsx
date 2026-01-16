// This file is part of OARepo-Requests
// Copyright (C) 2024 CESNET z.s.p.o.
//
// OARepo-Requests is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import {
  RequestLinksExtractor,
  InvenioRequestsAPI,
} from "@js/invenio_requests/api";
import { errorSerializer } from "@js/invenio_requests/api/serializers";
import { RequestActions } from "@js/invenio_requests/request/actions/RequestActions";
import PropTypes from "prop-types";
import { RequestActionContext } from "@js/invenio_requests/request/actions/context";
import React, { Component } from "react";
import { OarepoRequestsAPI } from "./OarepoRequestsApi";

export class RequestActionController extends Component {
  constructor(props) {
    super(props);
    const { request, requestApi } = props;
    this.linkExtractor = new RequestLinksExtractor(request);
    this.requestApi = requestApi || new OarepoRequestsAPI(this.linkExtractor);
    this.state = { modalOpen: {}, loading: false, error: undefined };
  }

  toggleActionModal = (actionId, val) => {
    const { modalOpen } = this.state;
    if (val) {
      modalOpen[actionId] = val;
    } else {
      modalOpen[actionId] = !modalOpen[actionId];
    }
    this.setState({ modalOpen: { ...modalOpen } });
  };

  performAction = async (action, commentContent) => {
    const { actionSuccessCallback, onBeforeAction, onError, formikRef } =
      this.props;

    // Extract form data from formik if available
    let formData = null;
    if (formikRef && formikRef.current) {
      const values = formikRef.current.values;
      if (values && Object.keys(values.payload).length > 0) {
        formData = { payload: values.payload };
      }
    }

    if (onBeforeAction) {
      try {
        const canProceed = await onBeforeAction(action, commentContent);

        if (!canProceed) {
          return;
        }
      } catch (error) {
        this.setState({ error: errorSerializer(error) });

        if (onError) {
          onError(errorSerializer(error));
        }
        return;
      }
    }

    this.setState({ loading: true });
    try {
      const specificAction = this.requestApi[action];
      const response =
        (await specificAction?.(formData)) ||
        (await this.requestApi.performAction(action, commentContent, formData));

      this.setState({ loading: false });
      this.toggleActionModal(action, false);
      actionSuccessCallback(response?.data);
    } catch (error) {
      console.error(error);
      const serializedError = errorSerializer(error);
      this.setState({ loading: false, error: serializedError });

      if (onError) {
        onError(serializedError);
      }
    }
  };

  cleanError = () => {
    this.setState({ error: undefined });
  };

  render() {
    const { modalOpen, error, loading } = this.state;
    const { request, children, size } = this.props;

    return (
      <RequestActionContext.Provider
        value={{
          modalOpen: modalOpen,
          toggleModal: this.toggleActionModal,
          linkExtractor: this.linkExtractor,
          requestApi: this.requestApi,
          performAction: this.performAction,
          cleanError: this.cleanError,
          error: error,
          loading: loading,
        }}
      >
        <RequestActions request={request} size={size} />
        {children}
      </RequestActionContext.Provider>
    );
  }
}

RequestActionController.propTypes = {
  request: PropTypes.object.isRequired,
  requestApi: PropTypes.oneOfType([
    PropTypes.instanceOf(InvenioRequestsAPI),
    PropTypes.instanceOf(OarepoRequestsAPI),
  ]),
  actionSuccessCallback: PropTypes.func,
  onBeforeAction: PropTypes.func,
  onError: PropTypes.func,
  formikRef: PropTypes.object,
  size: PropTypes.string,
  children: PropTypes.node,
};

RequestActionController.defaultProps = {
  requestApi: null,
  actionSuccessCallback: () => {},
  onBeforeAction: null,
  onError: null,
  formikRef: null,
  size: "medium",
  children: null,
};
