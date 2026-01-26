// This file is part of OARepo-Requests
// Copyright (C) 2024 CESNET z.s.p.o.
//
// OARepo-Requests is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.
import _set from "lodash/set";
import {
  RequestLinksExtractor,
  InvenioRequestsAPI,
} from "@js/invenio_requests/api";
import { RequestActions } from "./RequestActions";
import PropTypes from "prop-types";
import { RequestActionContext } from "@js/invenio_requests/request/actions/context";
import { useModalControlContext } from "./contexts";
import React, { useState, useMemo, useCallback, forwardRef } from "react";
import { OarepoRequestsAPI } from "./OarepoRequestsApi";

export const createFormikErrors = (requestPayloadErrors) => {
  if (!requestPayloadErrors || !Array.isArray(requestPayloadErrors)) {
    return {};
  }

  return requestPayloadErrors.reduce((errors, e) => {
    _set(errors, e.field, e.messages.join(" "));
    return errors;
  }, {});
};

export const RequestActionController = forwardRef(
  ({
    request,
    requestApi: requestApiProp,
    actionSuccessCallback,
    onBeforeAction,
    onErrorPlugins,
    formikRef,
    size,
    children,
    renderAllActions,
  }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(undefined);
    const linkExtractor = useMemo(
      () => new RequestLinksExtractor(request),
      [request]
    );
    const modalControlContext = useModalControlContext();
    const requestApi = useMemo(
      () => requestApiProp || new OarepoRequestsAPI(linkExtractor),
      [requestApiProp, linkExtractor]
    );

    const performAction = useCallback(
      async (action, commentContent) => {
        let formData = null;
        if (formikRef && formikRef.current) {
          const values = formikRef.current.values;
          if (values && Object.keys(values.payload).length > 0) {
            formData = { payload: values.payload };
          }
        }
        setLoading(true);
        const context = {
          action,
          request,
          modalControlContext,
          formikRef,
        };

        if (onBeforeAction) {
          try {
            const canProceed = await onBeforeAction(context);
            if (!canProceed) {
              return;
            }
          } catch (error) {
            setLoading(false);
            return;
          }
        }

        try {
          const specificAction = requestApi[action];
          const response =
            (await specificAction?.(action, undefined, formData)) ||
            (await requestApi.performAction(action, commentContent, formData));

          setLoading(false);
          actionSuccessCallback(response?.data, context);
        } catch (error) {
          const formikErrors =
            (error?.response?.data?.request_payload_errors?.length > 0 &&
              createFormikErrors(
                error?.response?.data?.request_payload_errors
              )) ||
            {};
          formikRef?.current?.setErrors({
            api: error?.response?.data?.message || error.message,
            ...formikErrors,
          });
          setLoading(false);
          setError(error);

          if (onErrorPlugins?.length > 0) {
            for (const plugin of onErrorPlugins) {
              const handled = plugin(error, context);
              if (handled) {
                return;
              }
            }
          }
        }
      },
      [
        formikRef,
        onBeforeAction,
        request,
        requestApi,
        actionSuccessCallback,
        onErrorPlugins,
        modalControlContext,
      ]
    );

    const cleanError = useCallback(() => {
      setError(undefined);
    }, []);

    const contextValue = useMemo(
      () => ({
        linkExtractor,
        requestApi,
        performAction,
        cleanError,
        error,
        loading,
        request: request,
      }),
      [
        linkExtractor,
        requestApi,
        performAction,
        cleanError,
        error,
        loading,
        request,
      ]
    );
    return (
      <RequestActionContext.Provider value={contextValue}>
        {renderAllActions && <RequestActions request={request} size={size} />}
        {children}
      </RequestActionContext.Provider>
    );
  }
);

RequestActionController.displayName = "RequestActionController";

RequestActionController.propTypes = {
  request: PropTypes.object.isRequired,
  requestApi: PropTypes.oneOfType([
    PropTypes.instanceOf(InvenioRequestsAPI),
    PropTypes.instanceOf(OarepoRequestsAPI),
  ]),
  actionSuccessCallback: PropTypes.func,
  onBeforeAction: PropTypes.func,
  onErrorPlugins: PropTypes.arrayOf(PropTypes.func),
  formikRef: PropTypes.object,
  size: PropTypes.string,
  children: PropTypes.node,
  renderAllActions: PropTypes.bool,
};

RequestActionController.defaultProps = {
  requestApi: null,
  actionSuccessCallback: () => {},
  onBeforeAction: null,
  formikRef: null,
  size: "medium",
  children: null,
  renderAllActions: true,
};
