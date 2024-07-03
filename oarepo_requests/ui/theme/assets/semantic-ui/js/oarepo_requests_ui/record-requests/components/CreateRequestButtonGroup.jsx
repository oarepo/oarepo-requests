import React from "react";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Segment, Header, Button, Placeholder, Message, Icon } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import { Formik } from "formik";

import { CreateModal } from "./modals";
import { mapPayloadUiToInitialValues } from "../utils";
import { useRecordContext } from "../contexts";

/**
 * @typedef {import("../types").Request} Request
 * @typedef {import("../types").RequestType} RequestType
 */

/**
 * @param {{ requestTypes: RequestType[], isLoading: boolean, loadingError: Error }} props
 */
export const CreateRequestButtonGroup = () => {
  const { record, recordLoading, recordLoadingError } = useRecordContext();
  const requestTypes = record?.expanded?.request_types ?? [];
  const createRequests = requestTypes.filter(requestType => requestType.links.actions?.create);

  return (
    <Segment className="requests-create-request-buttons borderless">
      <Header size="small" className="detail-sidebar-header">{i18next.t("Requests")}</Header>
      {recordLoading ?
        <Placeholder>
          {Array.from({ length: 2 }).map((_, index) => (
            <Placeholder.Paragraph key={index}>
              <Icon name="plus" disabled />
            </Placeholder.Paragraph>
          ))}
        </Placeholder> :
        recordLoadingError ?
          <Message negative>
            <Message.Header>{i18next.t("Error loading request types")}</Message.Header>
            <p>{recordLoadingError?.message}</p>
          </Message> :
          !_isEmpty(createRequests) ?
            <Button.Group vertical compact fluid>
              {createRequests.map((requestType) => (
                <Formik
                  key={requestType.type_id}
                  initialValues={
                    !_isEmpty(requestType?.payload) ?
                      { payload: requestType.payload } :
                      (requestType?.payload_ui ? mapPayloadUiToInitialValues(requestType?.payload_ui) : {})
                  }
                  onSubmit={() => { }} // We'll redefine with customSubmitHandler
                >
                  <CreateModal
                    requestType={requestType}
                    triggerElement={<Button icon="plus" className="pl-0" title={i18next.t(requestType.name)} basic compact content={requestType.name} />}
                  />
                </Formik>
              ))}
            </Button.Group> :
            <p>{i18next.t("No new requests to create")}.</p>
      }
    </Segment>
  );
}