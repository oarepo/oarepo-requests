import React, { createContext } from "react";

export const RecordContext = createContext();

export const RecordContextProvider = ({ children, record }) => {
  return (
    <RecordContext.Provider value={record}>
      {children}
    </RecordContext.Provider>
  );
};
