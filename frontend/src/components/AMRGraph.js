import React from "react";
import Network from "react-vis-network-graph";
import { amrToGraph } from "../utils/amrToGraph";

const AMRGraph = ({ amrText }) => {
  // Convert AMR text into nodes/edges
  const { nodes, edges } = amrToGraph(amrText);

  const graph = { nodes, edges };

  const options = {
    layout: {
      hierarchical: false,
    },
    physics: {
      enabled: true,
      stabilization: {
        iterations: 150,
      },
    },
    // Increase node shape size and font for better readability
    nodes: {
      shape: "ellipse",
      color: {
        background: "#cef",
        border: "#00f",
      },
      font: {
        size: 16, // Larger font size
        face: "Arial",
        color: "#333",
      },
      size: 25, // Larger node size
    },
    // Increase edge font size and set arrow heads
    edges: {
      arrows: { to: { enabled: true, scaleFactor: 1 } },
      color: "#333",
      font: {
        size: 14,
        face: "Arial",
        color: "#555",
      },
      smooth: false,
    },
  };

  const events = {
    select: ({ nodes, edges }) => {
      console.log("Selected nodes:", nodes);
      console.log("Selected edges:", edges);
    },
  };

  return (
    <div
      style={{
        width: "100%",
        height: "600px",
        border: "1px solid #ccc",
        marginBottom: "1rem",
      }}
    >
      <Network graph={graph} options={options} events={events} />
    </div>
  );
};

export default AMRGraph;
