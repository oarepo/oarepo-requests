import React from "react";
import PropTypes from "prop-types";

import { Button, Accordion } from "semantic-ui-react";
import _groupBy from "lodash/groupBy";
import _map from "lodash/map";
import _isNil from "lodash/isNil";
import _partition from "lodash/partition";
import _forEach from "lodash/forEach";

export const RequestButtons = ({ requests, mapRequestToModalComponent }) => {
  const [requestsWithCategory, requestsWithoutCategory] = _partition(requests, (request) => !_isNil(request?.category));

  const requestsWithoutCategoryGroup = _map(requestsWithoutCategory, mapRequestToModalComponent);

  const groupedRequests = _groupBy(requestsWithCategory, "category.value");
  
  let requestsInCategoryAlone = [];
  let requestsInCategoryMultiple = [];

  _forEach(groupedRequests, (requests) => {
    const requestModalTriggers = _map(requests, mapRequestToModalComponent);
    const category = requests[0].category; // All requests in the group have the same category
    
    if (requests.length === 1) {
      // If there's only one request in the category, return it directly
      requestsInCategoryAlone.push(requestModalTriggers[0]);
    } else {
      // If there are multiple requests in the category, return them as a Accordion with a ButtonGroup
      requestsInCategoryMultiple.push(
        <Accordion
          key={category.value}
          className="requests-per-category"
          defaultActiveIndex={0}
          styled
          panels={[
            {
              key: category.value,
              title: {
                content: category.label,
              },
              content: {
                content: (
                  <Button.Group vertical labeled icon fluid>
                    {requestModalTriggers}
                  </Button.Group>
                )
              },
            },
          ]}
        />
      );
    }
  });

  return (
    <>
      {requestsWithoutCategoryGroup}
      {requestsInCategoryAlone}
      {requestsInCategoryMultiple}
    </>
  );
};

RequestButtons.propTypes = {
  requests: PropTypes.arrayOf(PropTypes.object).isRequired,
  mapRequestToModalComponent: PropTypes.func.isRequired,
};
