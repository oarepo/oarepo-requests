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
import React, {
  useState,
  useMemo,
  useCallback,
  forwardRef,
  useImperativeHandle,
  useContext,
} from "react";
import { OarepoRequestsAPI } from "./OarepoRequestsApi";
import { OverridableContext } from "react-overridable";

export const RequestActionController = forwardRef(
  (
    {
      request,
      requestApi: requestApiProp,
      actionSuccessCallback,
      onBeforeAction,
      onError,
      formikRef,
      size,
      children,
      renderAllActions,
    },
    ref
  ) => {
    const [modalOpen, setModalOpen] = useState({});
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(undefined);

    const linkExtractor = useMemo(
      () => new RequestLinksExtractor(request),
      [request]
    );

    const requestApi = useMemo(
      () => requestApiProp || new OarepoRequestsAPI(linkExtractor),
      [requestApiProp, linkExtractor]
    );

    const toggleActionModal = useCallback((actionId, val) => {
      setModalOpen((prevModalOpen) => {
        const newModalOpen = { ...prevModalOpen };
        if (val !== undefined) {
          newModalOpen[actionId] = val;
        } else {
          newModalOpen[actionId] = !prevModalOpen[actionId];
        }
        return newModalOpen;
      });
    }, []);

    const performAction = useCallback(
      async (action, commentContent) => {
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
            const canProceed = await onBeforeAction(action, request);

            if (!canProceed) {
              return;
            }
          } catch (error) {
            const serializedError = errorSerializer(error);
            setError(serializedError);

            if (onError) {
              onError(serializedError);
            }
            return;
          }
        }

        setLoading(true);
        try {
          const specificAction = requestApi[action];
          const response =
            (await specificAction?.(formData)) ||
            (await requestApi.performAction(action, commentContent, formData));

          setLoading(false);
          toggleActionModal(action, false);
          actionSuccessCallback(response?.data);
        } catch (error) {
          console.error(error);
          setLoading(false);
          setError(error);

          if (onError) {
            onError(error);
          }
        }
      },
      [
        formikRef,
        onBeforeAction,
        request,
        onError,
        requestApi,
        toggleActionModal,
        actionSuccessCallback,
      ]
    );

    const cleanError = useCallback(() => {
      setError(undefined);
    }, []);

    // Expose state and methods to parent via ref
    useImperativeHandle(
      ref,
      () => ({
        loading,
        error,
        modalOpen,
        performAction,
        cleanError,
        toggleActionModal,
      }),
      [loading, error, modalOpen, performAction, cleanError, toggleActionModal]
    );

    const contextValue = useMemo(
      () => ({
        modalOpen,
        toggleModal: toggleActionModal,
        linkExtractor,
        requestApi,
        performAction,
        cleanError,
        error,
        loading,
        request: request,
      }),
      [
        modalOpen,
        toggleActionModal,
        linkExtractor,
        requestApi,
        performAction,
        cleanError,
        error,
        loading,
        request,
      ]
    );
    const overridableContext = useContext(OverridableContext);
    console.log(overridableContext, "dwadawdwadwadwadwadwadwadwaddwadwadwawa");
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
  onError: PropTypes.func,
  formikRef: PropTypes.object,
  size: PropTypes.string,
  children: PropTypes.node,
  renderAllActions: PropTypes.bool,
};

RequestActionController.defaultProps = {
  requestApi: null,
  actionSuccessCallback: () => {},
  onBeforeAction: null,
  onError: null,
  formikRef: null,
  size: "medium",
  children: null,
  renderAllActions: true,
};
