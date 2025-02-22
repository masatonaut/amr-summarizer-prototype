import React from "react";
import Network from "react-vis-network-graph";
import { amrToGraph } from "../utils/amrToGraph";

const AMRGraph = ({ amrText }) => {
  const { nodes, edges } = amrToGraph(amrText);

  const graph = { nodes, edges };

  const options = {
    layout: {
      hierarchical: {
        enabled: false,
      },
    },
    physics: {
      enabled: true,
      stabilization: {
        iterations: 150,
      },
      barnesHut: {
        gravitationalConstant: -20000,
        springConstant: 0.04,
        springLength: 95,
      },
    },
    nodes: {
      shape: "ellipse",
      color: {
        background: "#cef",
        border: "#00f",
      },
      font: {
        size: 14,
        face: "Arial",
        color: "#333",
      },
    },
    edges: {
      arrows: { to: { enabled: true, scaleFactor: 1 } },
      color: "#333",
      font: {
        size: 12,
        face: "Arial",
        color: "#555",
        strokeWidth: 0,
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
        width: "90%",
        height: "600px",
        margin: "0 auto",
        border: "1px solid #ccc",
      }}
    >
      <Network graph={graph} options={options} events={events} />
    </div>
  );
};

export default AMRGraph;
