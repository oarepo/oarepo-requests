import React, { createContext, useContext } from "react";
import { useConfirmDialog } from "../utils/hooks";
import PropTypes from "prop-types";

const ConfirmModalContext = createContext();

export const ConfirmModalContextProvider = ({
  children,
  isEventModal = false,
}) => {
  const confirmDialogStateAndHelpers = useConfirmDialog(isEventModal);
  return (
    <ConfirmModalContext.Provider value={confirmDialogStateAndHelpers}>
      {typeof children === "function"
        ? children(confirmDialogStateAndHelpers)
        : children}
    </ConfirmModalContext.Provider>
  );
};

ConfirmModalContextProvider.propTypes = {
  children: PropTypes.oneOfType([PropTypes.node, PropTypes.func]),
  isEventModal: PropTypes.bool,
};

export const useConfirmModalContext = () => {
  const context = useContext(ConfirmModalContext);
  if (!context) {
    throw new Error(
      "useModalControlContext must be used inside ConfirmModalContext.Provider"
    );
  }
  return context;
};
