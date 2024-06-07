import React, { useRef, useEffect } from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Button, Grid, List, Form, Divider, Comment, Header, Container, Icon, Menu, Loader, Segment } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import _sortBy from "lodash/sortBy";

import { ActionButtons, MainRequestDetails } from ".";

export const TopicPreview = ({ request }) => {
  const iframeRef = useRef(null);
  const [height, setHeight] = React.useState("0px");
  const [loading, setLoading] = React.useState(true);

  const iframeOnLoad = () => {
    setHeight(iframeRef.current.contentWindow.document.body.scrollHeight + "px");
    setLoading(false);
  }

  const selfHtml = request.topic.link.replace("/api", "") + "?embed=true";


  return (
    <Grid.Row>
      <Grid.Column>
        {loading && 
          <Segment placeholder loading className="borderless">
            <Loader active size="massive" />
          </Segment>
        }
        <iframe 
          ref={iframeRef} 
          src={selfHtml} 
          onLoad={iframeOnLoad} 
          title={request.topic.label + " record preview"} 
          width="100%" 
          height={height} 
          scrolling="no" 
          style={{
            outline: "none",
            border: "none",
            overflow: "hidden",
            margin: 0,
          }}
        />
      </Grid.Column>
    </Grid.Row>
  );
}
