import { useState } from "react";
import ImageUpload from "../components/ImageUpload";
import DetectionResult from "../components/DetectionResult";
import { Container, Typography,Box  } from "@mui/material";

const Home = () => {
  const [result, setResult] = useState(null);

  return (
    <Container
      maxWidth="md"
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        mt: 6,
      }}
    >
      <Typography
        variant="h3"
        align="center"
        sx={{
          fontWeight: "bold",
          letterSpacing: "0.5px",
          mb: 4,
          background: "linear-gradient(90deg, #00c6ff 0%, #0072ff 100%)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
        }}
      >
        AI Image Detection Dashboard
      </Typography>
      <ImageUpload setResult={setResult} />
       {/* Detection Result Section */}
      {result && (
        <Box sx={{ width: "100%", mt: 4 }}>
          <DetectionResult result={result} />
        </Box>
      )}
    </Container>
    
  );
};

export default Home;
