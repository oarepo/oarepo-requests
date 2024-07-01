import React, { createContext, useContext } from "react";

const RequestContext = createContext();

export const RequestContextProvider = ({ children, requests }) => {
  return (
    <RequestContext.Provider value={requests}>
      {children}
    </RequestContext.Provider>
  );
};

export const useRequestContext = () => {
  return useContext(RequestContext);
}