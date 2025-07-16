import React from "react";
import PropTypes from "prop-types";

import { Button, Accordion } from "semantic-ui-react";
import _groupBy from "lodash/groupBy";
import _map from "lodash/map";
import _isNil from "lodash/isNil";
import _partition from "lodash/partition";

export const RequestsPerCategory = ({ requests, mapRequestToModalComponent }) => {
  const [requestsWithCategory, requestsWithoutCategory] = _partition(requests, (request) => !_isNil(request?.category));

  const groupedRequests = _groupBy(requestsWithCategory, "category");

  const requestsWithoutCategoryGroup = _map(requestsWithoutCategory, mapRequestToModalComponent);

  const requestsPerCategoryAccordions = _map(groupedRequests, (requests, category) => {
    const requestModalTriggers = _map(requests, mapRequestToModalComponent);
    return (
      <Accordion
        key={category}
        className="requests-per-category"
        defaultActiveIndex={0}
        styled
        panels={[
          {
            key: category,
            title: {
              content: category,
            },
            content: {
              content: (
                <Button.Group vertical labeled icon fluid attached="bottom">
                  {requestModalTriggers}
                </Button.Group>
              )
            },
          },
        ]}
      />
    );
  });

  return (
    <>
      {requestsWithoutCategoryGroup}
      {requestsPerCategoryAccordions}
    </>
  );
};

RequestsPerCategory.propTypes = {
  requests: PropTypes.arrayOf(PropTypes.object).isRequired,
  mapRequestToModal: PropTypes.func.isRequired,
};
