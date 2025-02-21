import React, { useState } from "react";

function InputForm() {
  const [summary, setSummary] = useState("");
  const [article, setArticle] = useState("");
  const [responseData, setResponseData] = useState(null);
  const [error, setError] = useState(null);

  // Read the API URL from your .env file
  const API_BASE_URL = process.env.REACT_APP_API_URL;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/process_text`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ summary, article }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      const data = await response.json();
      setResponseData(data);
    } catch (err) {
      console.error("Error:", err);
      setError("Error sending data to the server");
    }
  };

  return (
    <div>
      <h2>Submit Text Data</h2>
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
      {responseData && (
        <div>
          <h3>Response:</h3>
          <p>
            <strong>Summary:</strong> {responseData.received_summary}
          </p>
          <p>
            <strong>Article:</strong> {responseData.received_article}
          </p>
        </div>
      )}
    </div>
  );
}

export default InputForm;
