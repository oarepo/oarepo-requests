// This file is part of OARepo-Requests
// Copyright (C) 2024 CESNET z.s.p.o.
//
// OARepo-Requests is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { InvenioRequestsAPI } from "@js/invenio_requests/api";
import { http } from "react-invenio-forms";
import _isEmpty from "lodash/isEmpty";

export class OarepoRequestsAPI extends InvenioRequestsAPI {
  constructor(requestLinksExtractor) {
    super(requestLinksExtractor);
    this.linksExtractor = requestLinksExtractor;
  }

  /**
   * Create a new request with payload data
   * @param {Object} formData - Form data in format {payload: {key: value}}
   * @returns {Promise} Response with created request
   */
  create = async (action, comment, formData) => {
    const createLink = this.linksExtractor.actions.create;
    if (!createLink) {
      throw new Error("Create action link is missing");
    }

    return await http.post(createLink, formData, {
      params: { expand: 1 },
    });
  };

  /**
   * Save an existing request (PUT to self link)
   * @param {Object} formData - Form data in format {payload: {key: value}}
   * @returns {Promise} Response with updated request
   */
  save = async (action, comment, formData) => {
    const selfLink = this.linksExtractor.self;
    if (!selfLink) {
      throw new Error("Self link is missing");
    }

    return await http.put(selfLink, formData, {
      params: { expand: 1 },
    });
  };

  /**
   * Create and immediately submit a request
   * @param {Object} formData - Form data in format {payload: {key: value}}
   * @returns {Promise} Response after submission
   */
  submit = async (action, comment, formData) => {
    // First create the request
    const createLink = this.linksExtractor.actions.create;
    if (createLink) {
      const createResponse = await this.create("create", undefined, formData);
      const submitLink = createResponse?.data?.links?.actions?.submit;
      if (!submitLink) {
        throw new Error("Submit link not found in create response");
      }
      return await http.post(
        submitLink,
        {},
        {
          params: { expand: 1 },
        }
      );
    } else {
      const saveLink = this.linksExtractor.self;
      if (formData && !_isEmpty(formData)) {
        await this.save("save", undefined, formData);
      }
      const submitLink = this.linksExtractor.actions.submit;
      return await http.post(
        submitLink,
        {},
        {
          params: { expand: 1 },
        }
      );
    }
  };
}
