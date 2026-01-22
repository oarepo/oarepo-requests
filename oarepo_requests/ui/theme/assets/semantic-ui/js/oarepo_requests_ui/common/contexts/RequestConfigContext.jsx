import React, { createContext, useContext, useMemo } from "react";
import PropTypes from "prop-types";
import { useQuery } from "@tanstack/react-query";
import { httpApplicationJson } from "@js/oarepo_ui";

const RequestConfigContext = createContext();

export const RequestConfigContextProvider = ({ children, requestTypeId }) => {
  const { data, isLoading, error } = useQuery(
    ["requestTypeConfig", requestTypeId],
    () => httpApplicationJson.get(`/requests/configs/${requestTypeId}`),
    {
      enabled: !!requestTypeId,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    }
  );

  const value = useMemo(
    () => ({
      requestTypeConfig: data?.data,
      isLoading,
      error,
    }),
    [data, isLoading, error]
  );

  return (
    <RequestConfigContext.Provider value={value}>
      {children}
    </RequestConfigContext.Provider>
  );
};

RequestConfigContextProvider.propTypes = {
  children: PropTypes.node,
  requestTypeId: PropTypes.string,
};

export const useRequestConfigContext = () => {
  const context = useContext(RequestConfigContext);
  if (!context) {
    console.warn(
      "useRequestConfigContext must be used inside RequestConfigContext.Provider"
    );
  }
  return context;
};
