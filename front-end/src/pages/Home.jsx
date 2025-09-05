
import { useState } from "react";
import ImageUpload from "../components/ImageUpload";
import DetectionResult from "../components/DetectionResult";
import { Container, Typography, Box } from "@mui/material";

const Home = () => {
  const [result, setResult] = useState(null);

  return (
    <Box
      sx={{
        width: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        py: { xs: 0.5, sm: 1 },
      }}
    >
      <Box
        sx={{
          width: "100%",
          maxWidth: { xs: 360, sm: 500, md: 600 },
          mx: "auto",
          background: "#fff",
          borderRadius: 5,
          boxShadow: "0 8px 40px rgba(0,0,0,0.10)",
          p: { xs: 1.5, sm: 3 },
          mb: 2,
        }}
      >
        <Typography
          variant="h3"
          align="center"
          sx={{
            fontWeight: 800,
            letterSpacing: "0.5px",
            mb: 2,
            color: "#1976d2",
            textShadow: "0 2px 8px rgba(25,118,210,0.08)",
          }}
        >
          AI Image Detection Dashboard
        </Typography>
        <ImageUpload setResult={setResult} />
      </Box>
      {/* Detection Result Section */}
      {result && (
  <Box sx={{ width: "100%", maxWidth: { xs: 360, sm: 500, md: 600 }, mx: "auto", mb: 2 }}>
          <DetectionResult result={result} />
        </Box>
      )}
    </Box>
  );
};

export default Home;
