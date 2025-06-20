import React, { useState, Component } from "react";
import PropTypes from "prop-types";
import { Modal, Button, Grid, Icon, Popup } from "semantic-ui-react";
import { OverridableContext, overrideStore } from "react-overridable";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import {
  BucketAggregation,
  EmptyResults,
  Error,
  ReactSearchKit,
  ResultsLoader,
  withState,
  InvenioSearchApi,
  Count,
  Pagination,
  ResultsList,
  ResultsPerPage,
  Sort,
} from "react-searchkit";
import {
  CountElement,
  SearchappSearchbarElement,
  ResultsPerPageLabel,
} from "@js/oarepo_ui/search";
import { ComputerTabletRequestsListItem } from "@js/oarepo_requests_common/search/ComputerTabletRequestsListItem";
import { MobileRequestsListItem } from "@js/oarepo_requests_common/search/MobileRequestsListItem";
import { defaultContribComponents } from "@js/invenio_requests/contrib";
import { requestTypeSpecificComponents } from "@js/oarepo_requests_common/search/RequestTypeSpecificComponents";
import {
  ContribBucketAggregationElement,
  ContribBucketAggregationValuesElement,
} from "@js/invenio_search_ui/components";

function RequestsResultsItem({ result }) {
  const ComputerTabletRequestsItemWithState = withState(
    ComputerTabletRequestsListItem
  );
  const MobileRequestsItemWithState = withState(MobileRequestsListItem);
  const detailPageUrl = result?.links?.self_html;
  return (
    <>
      <ComputerTabletRequestsItemWithState
        result={result}
        detailsURL={detailPageUrl}
      />
      <MobileRequestsItemWithState result={result} detailsURL={detailPageUrl} />
    </>
  );
}

export class Results extends Component {
  constructor(props) {
    super(props);

    const { sortValues, resultsPerPageValues } = this.props;

    this.sortValues = sortValues;
    this.resultsPerPageValues = resultsPerPageValues;
  }

  render() {
    const { currentResultsState } = this.props;
    const { data } = currentResultsState;
    const { total } = data;
    return total ? (
      <React.Fragment>
        <Grid relaxed verticalAlign="middle">
          <Grid.Column width={8}>
            <Count />
          </Grid.Column>
          <Grid.Column width={8} textAlign="right">
            <Sort values={this.sortValues} />
          </Grid.Column>
        </Grid>
        <Grid relaxed>
          <Grid.Column width={16}>
            <ResultsList />
          </Grid.Column>
        </Grid>
        <Grid relaxed verticalAlign="middle" textAlign="center">
          <Grid.Column width={8}>
            <Pagination
              options={{ size: "tiny" }}
              showWhenOnlyOnePage={false}
            />
          </Grid.Column>
          <Grid.Column width={8} textAlign="right">
            <ResultsPerPage
              values={this.resultsPerPageValues}
              label={ResultsPerPageLabel}
            />
          </Grid.Column>
        </Grid>
      </React.Fragment>
    ) : null;
  }
}

Results.propTypes = {
  currentResultsState: PropTypes.object.isRequired,
  sortValues: PropTypes.array.isRequired,
  resultsPerPageValues: PropTypes.array.isRequired,
};

const overriddenComponents = {
  "RecordRequestsSearch.ResultsList.item": RequestsResultsItem,
  "RecordRequestsSearch.Count.element": CountElement,
  "RecordRequestsSearch.BucketAggregationValues.element":
    ContribBucketAggregationValuesElement,
  "RecordRequestsSearch.BucketAggregation.element":
    ContribBucketAggregationElement,
  ...defaultContribComponents,
  ...requestTypeSpecificComponents,
  ...overrideStore.getAll(),
};
const OnResults = withState(Results);

const sortValues = [
  { text: i18next.t("Newest"), sortBy: "newest" },
  { text: i18next.t("Oldest"), sortBy: "oldest" },
];

const resultsPerPageValues = [
  { text: "10", value: 10 },
  { text: "20", value: 20 },
  { text: "50", value: 50 },
];

export const RecordRequestsListModal = ({ endpointUrl, trigger }) => {
  const [modalOpen, setModalOpen] = useState(false);

  const searchApi = new InvenioSearchApi({
    axios: {
      url: endpointUrl,
      timeout: 5000,
      headers: { Accept: "application/vnd.inveniordm.v1+json" },
    },
  });

  const initialState = {
    sortBy: "bestmatch",
    sortOrder: "asc",
    layout: "list",
    page: 1,
    size: 10,
  };

  return (
    <Modal
      open={modalOpen}
      onOpen={() => setModalOpen(true)}
      onClose={() => setModalOpen(false)}
      size="large"
      trigger={
        trigger || (
          <Button
            title={i18next.t("Search Record Requests")}
            className="transparent"
            icon="eye"
            onClick={() => setModalOpen(true)}
          ></Button>
        )
      }
    >
      <Modal.Header>
        {i18next.t("Record requests")}{" "}
        <Popup
          position="top center"
          content={
            <span className="helptext">
              {i18next.t("Request history of the record.")}
            </span>
          }
          trigger={
            <Icon className="ml-5" name="question circle outline"></Icon>
          }
        />
      </Modal.Header>
      <Modal.Content>
        <OverridableContext.Provider value={overriddenComponents}>
          <ReactSearchKit
            appName="RecordRequestsSearch"
            searchApi={searchApi}
            initialQueryState={initialState}
            defaultSortingOnEmptyQueryString={{
              sortBy: "newest",
            }}
            urlHandlerApi={{ enabled: false }}
          >
            <React.Fragment>
              <Grid>
                <Grid.Row>
                  <Grid.Column width={16}>
                    <SearchappSearchbarElement
                      placeholder={i18next.t("Search record requests...")}
                    />
                  </Grid.Column>
                </Grid.Row>
              </Grid>
              <Grid relaxed className="computer tablet only">
                <Grid.Row columns={2}>
                  <Grid.Column width={6}>
                    <BucketAggregation
                      title={i18next.t("Typ")}
                      agg={{
                        field: "type",
                        aggName: "type",
                      }}
                    />
                    <BucketAggregation
                      title={i18next.t("Stav žádosti")}
                      agg={{
                        field: "status",
                        aggName: "status",
                      }}
                    />
                  </Grid.Column>
                  <Grid.Column width={10}>
                    <ResultsLoader loading>
                      <EmptyResults />
                      <Error />
                      <OnResults
                        sortValues={sortValues}
                        resultsPerPageValues={resultsPerPageValues}
                      />
                    </ResultsLoader>
                  </Grid.Column>
                </Grid.Row>
              </Grid>
              <Grid relaxed className="mobile only">
                <Grid.Row columns={1}>
                  <Grid.Column width={16}>
                    <ResultsLoader>
                      <EmptyResults />
                      <Error />
                      <OnResults
                        sortValues={sortValues}
                        resultsPerPageValues={resultsPerPageValues}
                      />
                    </ResultsLoader>
                  </Grid.Column>
                </Grid.Row>
              </Grid>
            </React.Fragment>
          </ReactSearchKit>
        </OverridableContext.Provider>
      </Modal.Content>
      <Modal.Actions>
        <Button onClick={() => setModalOpen(false)}>
          {i18next.t("Close")}
        </Button>
      </Modal.Actions>
    </Modal>
  );
};

RecordRequestsListModal.propTypes = {
  endpointUrl: PropTypes.string.isRequired,
  trigger: PropTypes.node,
  componentOverrides: PropTypes.object,
};

export default RecordRequestsListModal;
