import React from "react";
import Network from "react-vis-network-graph";
import { amrToGraph } from "../utils/amrToGraph";

const AMRGraph = ({ amrText }) => {
  // Convert AMR text into nodes and edges using your utility function.
  const { nodes, edges } = amrToGraph(amrText);

  // Create a graph object in the format expected by react-vis-network-graph.
  const graph = {
    nodes: nodes,
    edges: edges,
  };

  // Options for the network graph. Adjust as needed.
  const options = {
    layout: {
      hierarchical: false,
    },
    edges: {
      color: "#000000",
      arrows: {
        to: { enabled: true },
      },
    },
    physics: {
      enabled: true,
    },
  };

  // Optional event handlers (e.g., for selection)
  const events = {
    select: ({ nodes, edges }) => {
      console.log("Selected nodes:", nodes);
      console.log("Selected edges:", edges);
    },
  };

  return (
    <div style={{ height: "400px", border: "1px solid #ccc" }}>
      <Network graph={graph} options={options} events={events} />
    </div>
  );
};

export default AMRGraph;
