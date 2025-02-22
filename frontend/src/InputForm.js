// frontend/src/InputForm.js
import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { useNavigate, useLocation, Link } from "react-router-dom";

const InputForm = () => {
  const [summary, setSummary] = useState("");
  const [article, setArticle] = useState("");
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/process_amr`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ summary, article }),
        }
      );

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const amrData = await response.json();
      // Navigate to the results page and pass the AMR data via state
      navigate("/results", { state: { amrData } });
    } catch (err) {
      console.error("Error:", err);
      setError("Error processing your request.");
    }
  };

  return (
    <div>
      <h2>Enter Your Text</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Summary:</label>
          <br />
          <textarea
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            rows="4"
            cols="50"
          />
        </div>
        <div>
          <label>Article:</label>
          <br />
          <textarea
            value={article}
            onChange={(e) => setArticle(e.target.value)}
            rows="8"
            cols="50"
          />
        </div>
        <button type="submit">Submit</button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
};

export default InputForm;
