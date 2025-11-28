import React from "react";
import _isEmpty from "lodash/isEmpty";
import PropTypes from "prop-types";
import { Grid } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_requests/i18next";
import { RequestActionButton } from "../components/RequestAction";

export const requestButtonsDefaultIconConfig = {
  delete_published_record: { icon: "trash" },
  publish_draft: { icon: "upload" },
  publish_new_version: { icon: "upload" },
  publish_changed_metadata: { icon: "upload" },
  new_version: { icon: "tag" },
  edit_published_record: { icon: "pencil" },
  assign_doi: { icon: "address card" },
  delete_doi: { icon: "remove" },
  created: { icon: "paper plane" },
  initiate_community_migration: { icon: "exchange" },
  confirm_community_migration: { icon: "exchange" },
  secondary_community_submission: { icon: "users" },
  remove_secondary_community: { icon: "remove" },
  submitted: { icon: "clock" },
  default: { icon: "plus" },
};

const EmptyRecordApplicableRequests = () => (
  <p>
    <i>
      <small>{i18next.t("This record has no user requests applicable.")}</small>
    </i>
  </p>
);

export const RecordRequests = ({
  record,
  applicableRequestsUrl = "/api/requests/applicable",
}) => {
  const [disabled, setDisabled] = React.useState(false);
  const applicableRequests = record.expanded.request_types;
  if (_isEmpty(applicableRequests)) {
    return <EmptyRecordApplicableRequests />;
  }
  console.log({ applicableRequests });
  return (
    <Grid columns={1} className="record-management">
      {applicableRequests.map((requestType) => (
        <Grid.Column key={requestType.type_id} className="pb-5">
          <RequestActionButton requestType={requestType} />
        </Grid.Column>
      ))}
    </Grid>
  );
};

RecordRequests.propTypes = {
  record: PropTypes.object.isRequired,
  applicableRequestsUrl: PropTypes.string,
};

export default RecordRequests;
