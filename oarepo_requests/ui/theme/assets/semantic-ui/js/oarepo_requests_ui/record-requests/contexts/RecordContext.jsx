import React, { createContext, useContext } from "react";

const RecordContext = createContext();

export const RecordContextProvider = ({ children, record }) => {
  return (
    <RecordContext.Provider value={record}>
      {children}
    </RecordContext.Provider>
  );
};

export const useRecordContext = () => {
  return useContext(RecordContext);
}