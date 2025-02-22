import React from "react";
import { Box } from "@mui/material";

const PageLayout = ({ children }) => {
  return (
    <Box
      sx={{
        maxWidth: 800,
        mx: "auto",
        mt: 4,
        p: 2,
        display: "flex",
        flexDirection: "column",
        gap: 2,
      }}
    >
      {children}
    </Box>
  );
};

export default PageLayout;
