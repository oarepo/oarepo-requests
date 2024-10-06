import React, { createContext, useContext } from "react";
import { useConfirmDialog } from "@js/oarepo_requests_common";
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
    console.error(
      "useModalControlContext must be used inside ConfirmModalContext.Provider"
    );
  }
  return context;
};
