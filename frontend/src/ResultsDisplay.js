import React from "react";
import { useLocation, Link as RouterLink } from "react-router-dom";
import { Box, Typography, Link } from "@mui/material";
import PageLayout from "./components/PageLayout";
import AMRGraph from "./components/AMRGraph";

const ResultsDisplay = () => {
  const location = useLocation();
  const { amrData } = location.state || {};

  if (!amrData) {
    return (
      <PageLayout>
        <Typography variant="h5" align="center" gutterBottom>
          No results to display.
        </Typography>
        <Link component={RouterLink} to="/" variant="body1">
          Back to Input
        </Link>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <Typography variant="h4" align="center" gutterBottom>
        AMR Parsing Results
      </Typography>

      {/* Summary AMR Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          Summary AMR
        </Typography>
        <AMRGraph amrText={amrData.summary_amr} />
      </Box>

      {/* Top Sentence AMRs Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          Top Sentence AMRs
        </Typography>
        {Object.entries(amrData.top_sentence_amrs).map(([sentence, amr]) => (
          <Box key={sentence} sx={{ mb: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              {sentence}
            </Typography>
            <AMRGraph amrText={amr} />
          </Box>
        ))}
      </Box>

      <Link component={RouterLink} to="/" variant="body1">
        Back to Input
      </Link>
    </PageLayout>
  );
};

export default ResultsDisplay;
