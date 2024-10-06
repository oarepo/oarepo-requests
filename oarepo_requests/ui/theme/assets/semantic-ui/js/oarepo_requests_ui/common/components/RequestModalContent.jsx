import React from "react";
import PropTypes from "prop-types";
import { Grid } from "semantic-ui-react";
import {} from "react-invenio-forms";
import {
  SideRequestInfo,
  Timeline,
} from "@js/oarepo_requests_detail/components";
import {
  REQUEST_MODAL_TYPE,
  RequestCustomFields,
} from "@js/oarepo_requests_common";
import { i18next } from "@translations/oarepo_requests_ui/i18next";

/**
 * @typedef {import("../../record-requests/types").Request} Request
 * @typedef {import("../../record-requests/types").RequestTypeEnum} RequestTypeEnum
 * @typedef {import("../../record-requests/types").Event} Event
 */

/** @param {{ request: Request, requestModalType: RequestTypeEnum, }} props */
export const RequestModalContent = ({
  request,
  customFields,
  modalActions,
}) => {
  /** @type {{requests: Request[], setRequests: (requests: Request[]) => void}} */

  const description = request?.stateful_description || request?.description;
  return (
    <Grid doubling stackable>
      <Grid.Row>
        {description && (
          <Grid.Column as="p" id="request-modal-desc">
            {description}{" "}
            <a
              href={request?.links?.self_html}
              target="_blank"
              rel="noopener noreferrer"
            >
              ({i18next.t("Request details")})
            </a>
          </Grid.Column>
        )}
      </Grid.Row>
      <Grid.Row>
        <Grid.Column>
          <SideRequestInfo request={request} />
        </Grid.Column>
      </Grid.Row>
      <RequestCustomFields
        request={request}
        customFields={customFields}
        actions={modalActions}
      />
      <Grid.Row>
        <Grid.Column>
          <Timeline request={request} />
        </Grid.Column>
      </Grid.Row>
    </Grid>
  );
};

RequestModalContent.propTypes = {
  request: PropTypes.object.isRequired,
  customFields: PropTypes.object,
  modalActions: PropTypes.array,
};
