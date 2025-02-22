// frontend/src/ResultsDisplay.js
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { useNavigate, useLocation, Link } from "react-router-dom";

const ResultsDisplay = () => {
  // Retrieve the AMR data passed via React Router state
  const location = useLocation();
  const { amrData } = location.state || {};

  if (!amrData) {
    return (
      <div>
        <h2>No results to display.</h2>
        <Link to="/">Back to Input</Link>
      </div>
    );
  }

  return (
    <div>
      <h2>AMR Parsing Results</h2>

      <section>
        <h3>Summary AMR</h3>
        <pre>{amrData.summary_amr}</pre>
      </section>

      <section>
        <h3>Top Sentence AMRs</h3>
        {Object.entries(amrData.top_sentence_amrs).map(([sentence, amr]) => (
          <div key={sentence} style={{ marginBottom: "1rem" }}>
            <h4>{sentence}</h4>
            <pre>{amr}</pre>
          </div>
        ))}
      </section>

      <Link to="/">Back to Input</Link>
    </div>
  );
};

export default ResultsDisplay;
