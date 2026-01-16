import React, { createContext, useContext, useRef } from "react";
import PropTypes from "prop-types";

const FormikRefContext = createContext();

export const FormikRefContextProvider = ({ children, value }) => {
  const formikRef = useRef();
  return (
    <FormikRefContext.Provider value={formikRef}>
      {children}
    </FormikRefContext.Provider>
  );
};

FormikRefContextProvider.propTypes = {
  value: PropTypes.object.isRequired,
  children: PropTypes.node,
};

export const useFormikRefContext = () => {
  const context = useContext(FormikRefContext);
  if (!context) {
    console.warn(
      "useFormikRefContext must be used inside FormikRefContext.Provider"
    );
  }
  return context;
};
