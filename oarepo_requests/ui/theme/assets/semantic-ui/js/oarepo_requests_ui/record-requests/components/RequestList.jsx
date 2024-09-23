import React from "react";
import PropTypes from "prop-types";

import { Button } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";

import { RequestModal, RequestModalContent } from ".";

/**
 * @typedef {import("../types").Request} Request
 */

/**
 * @param {{ requests: Request[] }} props
 */
export const RequestList = ({ requests }) => {
  return requests.map((request) => {
    const header = !_isEmpty(request?.title)
      ? request.title
      : !_isEmpty(request?.name)
      ? request.name
      : request.type;
    return (
      <RequestModal
        key={request.id}
        request={request}
        requestType={request}
        header={header}
        requestCreationModal={false}
        trigger={
          <Button
            className={`block request-reply-button ${request.type} mb-10`}
            fluid
            title={header}
            content={header}
            icon={request?.status_code === "created" ? "paper plane" : "clock"}
            labelPosition="left"
          />
        }
        ContentComponent={RequestModalContent}
      />
    );
  });
};

RequestList.propTypes = {
  requests: PropTypes.array.isRequired,
};
