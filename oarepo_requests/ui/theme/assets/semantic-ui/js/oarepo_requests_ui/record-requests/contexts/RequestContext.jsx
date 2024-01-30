import React, { createContext } from "react";

export const RequestContext = createContext();

export const RequestContextProvider = ({ children, requests }) => {
  return (
    <RequestContext.Provider value={requests}>
      {children}
    </RequestContext.Provider>
  );
};
