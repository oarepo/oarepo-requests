import { RequestActionContext } from "@js/invenio_requests/request/actions/context";
import { useContext } from "react";

export const useRequestActionContext = () => {
  const context = useContext(RequestActionContext);
  if (!context) {
    console.warn(
      "useRequestActionContext must be used inside RequestActionContext.Provider"
    );
  }
  return context;
};
