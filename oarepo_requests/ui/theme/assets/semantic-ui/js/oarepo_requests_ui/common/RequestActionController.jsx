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
import { errorSerializer } from "@js/invenio_requests/api/serializers";
import { RequestActions } from "./RequestActions";
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
        setLoading(true);

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
            setLoading(false);
            return;
          }
        }

        try {
          const specificAction = requestApi[action];
          console.log(specificAction, "specificActionspecificAction");
          const response =
            (await specificAction?.(action, undefined, formData)) ||
            (await requestApi.performAction(action, commentContent, formData));

          setLoading(false);
          toggleActionModal(action, false);
          actionSuccessCallback(response?.data);
        } catch (error) {
          console.error(error, "dwadwadawdwadadadwad");
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
          toggleActionModal(action, false);
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
