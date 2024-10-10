import React from "react";
import PropTypes from "prop-types";

export const DefaultView = ({ props, value }) => {
  return <span {...props}>{value}</span>;
};

DefaultView.propTypes = {
  props: PropTypes.object,
  value: PropTypes.string,
};
