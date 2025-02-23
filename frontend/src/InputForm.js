import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Box, TextField, Button, Typography } from "@mui/material";
import PageLayout from "./components/PageLayout";

const InputForm = () => {
  const [summary, setSummary] = useState("");
  const [article, setArticle] = useState("");
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // Client-side input validation: Ensure both fields are filled in
    if (!summary.trim() || !article.trim()) {
      setError("Both Summary and Article are required.");
      return;
    }

    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/process_amr`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ summary, article }),
        }
      );

      if (!response.ok) {
        // Extract error message from the response, if available
        const errorData = await response.json();
        throw new Error(errorData.detail || "Network response was not ok");
      }

      const amrData = await response.json();
      // Navigate to the results page and pass the AMR data via state
      navigate("/results", { state: { amrData } });
    } catch (err) {
      console.error("Error:", err);
      setError(err.message || "Error processing your request.");
    }
  };

  return (
    <PageLayout>
      <Typography variant="h4" align="center" gutterBottom>
        Enter Your Text
      </Typography>

      <Box
        component="form"
        onSubmit={handleSubmit}
        sx={{ display: "flex", flexDirection: "column", gap: 2 }}
      >
        <TextField
          label="Summary"
          variant="outlined"
          multiline
          rows={4}
          value={summary}
          onChange={(e) => setSummary(e.target.value)}
        />
        <TextField
          label="Article"
          variant="outlined"
          multiline
          rows={8}
          value={article}
          onChange={(e) => setArticle(e.target.value)}
        />
        <Button
          type="submit"
          variant="contained"
          color="primary"
          sx={{ alignSelf: "flex-start" }}
        >
          Submit
        </Button>
      </Box>

      {error && (
        <Typography variant="body1" color="error" align="center" sx={{ mt: 2 }}>
          {error}
        </Typography>
      )}
    </PageLayout>
  );
};

export default InputForm;
