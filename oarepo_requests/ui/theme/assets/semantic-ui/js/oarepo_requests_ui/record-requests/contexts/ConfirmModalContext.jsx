import React, { createContext, useContext } from "react";
import { useConfirmDialog } from "../utils/hooks";

const ConfirmModalContext = createContext();

export const ConfirmModalContextProvider = ({ children, isEventModal = false }) => {
  const confirmDialogStateAndHelpers = useConfirmDialog(isEventModal);
  return (
    <ConfirmModalContext.Provider value={confirmDialogStateAndHelpers}>
      {typeof children === 'function'
        ? children(confirmDialogStateAndHelpers)
        : children}
    </ConfirmModalContext.Provider>
  );
};

export const useConfirmModalContext = () => {
  return useContext(ConfirmModalContext);
};