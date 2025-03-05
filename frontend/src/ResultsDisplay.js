import React from "react";
import { useLocation, Link as RouterLink } from "react-router-dom";
import { Box, Typography, Link } from "@mui/material";
import PageLayout from "./components/PageLayout";

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

      {/* Summary AMR SVG Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          Summary AMR
        </Typography>
        {amrData.summary_svg ? (
          <div
            dangerouslySetInnerHTML={{ __html: amrData.summary_svg }}
            style={{ border: "1px solid #ccc", padding: "1rem" }}
          />
        ) : (
          <Typography>No summary AMR available.</Typography>
        )}
      </Box>

      {/* Top Sentence AMR SVGs Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          Top Sentence AMRs
        </Typography>
        {amrData.top_sentence_amrs &&
        Object.entries(amrData.top_sentence_amrs).length > 0 ? (
          Object.entries(amrData.top_sentence_amrs).map(([sentence, svg]) => (
            <Box key={sentence} sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                {sentence}
              </Typography>
              {svg ? (
                <div
                  dangerouslySetInnerHTML={{ __html: svg }}
                  style={{ border: "1px solid #ccc", padding: "1rem" }}
                />
              ) : (
                <Typography>No AMR available for this sentence.</Typography>
              )}
            </Box>
          ))
        ) : (
          <Typography>No top sentence AMRs available.</Typography>
        )}
      </Box>

      <Link component={RouterLink} to="/" variant="body1">
        Back to Input
      </Link>
    </PageLayout>
  );
};

export default ResultsDisplay;
