import React from "react";
import PropTypes from "prop-types";

export default function DefaultView({ props, value }) {
  return <span {...props}>{value}</span>
}
