import React from "react";

import { Grid } from "semantic-ui-react";
import IframeResizer from "@iframe-resizer/react";

export const TopicPreview = ({ request }) => {
  return (
    <Grid.Row>
      <Grid.Column>
        <IframeResizer
          license='GPLv3'
          src={request.topic.links.self_html + "?embed=true"} 
          title={request.topic.label + " record preview"} 
          style={{
            width: '100%',
            height: '100vh',
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
