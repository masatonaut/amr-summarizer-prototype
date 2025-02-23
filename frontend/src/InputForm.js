import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  TextField,
  Button,
  Typography,
  CircularProgress,
} from "@mui/material";
import PageLayout from "./components/PageLayout";

const MAX_SUMMARY_LENGTH = 2000;
const MAX_ARTICLE_LENGTH = 10000;

const InputForm = () => {
  const [summary, setSummary] = useState("");
  const [article, setArticle] = useState("");
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // Client-side input validation: trim whitespace and check for emptiness.
    const summaryClean = summary.trim();
    const articleClean = article.trim();
    if (!summaryClean || !articleClean) {
      setError("Both Summary and Article are required.");
      return;
    }
    if (summaryClean.length > MAX_SUMMARY_LENGTH) {
      setError("Summary is too long. Please reduce your input.");
      return;
    }
    if (articleClean.length > MAX_ARTICLE_LENGTH) {
      setError("Article is too long. Please reduce your input.");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/process_amr`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            summary: summaryClean,
            article: articleClean,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Network response was not ok");
      }

      const amrData = await response.json();
      // Navigate to the results page and pass the AMR data via state.
      navigate("/results", { state: { amrData } });
    } catch (err) {
      console.error("Error:", err);
      setError(err.message || "Error processing your request.");
    }
    setIsLoading(false);
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
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={isLoading}
          >
            Submit
          </Button>
          {isLoading && <CircularProgress size={24} />}
        </Box>
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
