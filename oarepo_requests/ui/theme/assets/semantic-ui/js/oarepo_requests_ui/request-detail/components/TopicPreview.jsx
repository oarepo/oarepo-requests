import React, { useRef } from "react";

import { Grid, Loader, Segment } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import _sortBy from "lodash/sortBy";

export const TopicPreview = ({ request }) => {
  const iframeRef = useRef(null);
  const [height, setHeight] = React.useState("0px");
  const [loading, setLoading] = React.useState(true);

  const iframeOnLoad = () => {
    setHeight(iframeRef.current.contentWindow.document.body.scrollHeight + "px");
    setLoading(false);
  }

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
          src={request.topic.links.self_html} 
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
