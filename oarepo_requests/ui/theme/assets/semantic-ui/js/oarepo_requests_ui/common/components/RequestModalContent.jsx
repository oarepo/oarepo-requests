import React from "react";
import PropTypes from "prop-types";
import { Grid } from "semantic-ui-react";
import {
  SideRequestInfo,
  RequestCustomFields,
  Timeline,
} from "@js/oarepo_requests_common";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import sanitizeHtml from "sanitize-html";

/**
 * @typedef {import("../../record-requests/types").Request} Request
 */

/** @param {{ request: Request }} props */
export const RequestModalContent = ({
  request,
  customFields,
  allowedHtmlAttrs,
  allowedHtmlTags,
}) => {
  const description = request?.stateful_description || request?.description;

  const sanitizedDescription = sanitizeHtml(description, {
    allowedTags: allowedHtmlTags,
    allowedAttributes: allowedHtmlAttrs,
  });

  return (
    <Grid doubling stackable>
      <Grid.Row>
        {description && (
          <Grid.Column as="p" id="request-modal-desc">
            <span dangerouslySetInnerHTML={{ __html: sanitizedDescription }} />{" "}
            {request?.links?.self_html && (
              <a
                href={request.links.self_html}
                target="_blank"
                rel="noopener noreferrer"
              >
                ({i18next.t("Request details")})
              </a>
            )}
          </Grid.Column>
        )}
      </Grid.Row>
      <Grid.Row>
        <Grid.Column>
          <SideRequestInfo request={request} />
        </Grid.Column>
      </Grid.Row>
      <RequestCustomFields request={request} customFields={customFields} />
      <Grid.Row>
        <Grid.Column>
          <Timeline request={request} />
        </Grid.Column>
      </Grid.Row>
    </Grid>
  );
};

/* eslint-disable react/require-default-props */
RequestModalContent.propTypes = {
  request: PropTypes.object.isRequired,
  customFields: PropTypes.object,
  allowedHtmlAttrs: PropTypes.object,
  allowedHtmlTags: PropTypes.array,
};
/* eslint-enable react/require-default-props */
