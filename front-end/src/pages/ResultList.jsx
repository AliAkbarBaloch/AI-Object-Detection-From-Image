import React, { useEffect, useState } from "react";
import { getPreviousResults } from "../api/imageApi"; // adjust path // your axios instance
import { useLocation, useNavigate } from "react-router-dom";
import {
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  TextField,
} from "@mui/material";


const ResultsPage = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const location = useLocation();
  const dat = location.state?.result;
  const navigate = useNavigate();

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const data = await getPreviousResults();
        console.log(data.results)
        setResults(data.results || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
        
      }
    };

    fetchResults();
  }, []);



  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <Box sx={{ p: 4 }}>
     <Box
        sx={{
          maxWidth: 800,
          mx: "auto",
          mb: 4,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          px: 7,
        }}
      >
        {/* Title Card */}
        <Card
  sx={{
    flexGrow: 1,
    maxWidth: 100, // smaller width
    maxHeight: 100, // smaller height
    
    backgroundColor: "#f5f5f7",
    color: "#111",
    borderRadius: 3,
    padding: 0,
    boxShadow: "0 4px 15px rgba(0,0,0,0.1)",
    textAlign: "center",
  }}
>
  <CardContent sx={{ p: 1 }}>
    <Typography
      variant="subtitle1"
      sx={{
        fontWeight: 700,
        fontSize: "1rem", // smaller font
      }}
    >
      Previous Results
    </Typography>
  </CardContent>
</Card>


        {/* Home Button */}
        <Button
          variant="contained"
          onClick={() => navigate("/home")}
          sx={{
            ml: 3,
            background: "linear-gradient(135deg,#1976d2,#0d47a1)",
            fontWeight: 700,
            px: 3,
            py: 1,
            borderRadius: 2,
            transition: "all 0.3s ease",
            boxShadow: "0 4px 15px rgba(25, 118, 210, 0.3)",
            "&:hover": {
              boxShadow: "0 8px 22px rgba(25, 118, 210, 0.35)",
              transform: "translateY(-2px)",
            },
          }}
        >
          Home
        </Button>
      </Box>
      <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
  {results.map((result) => (
    <Card
      key={result._id}
      sx={{
        maxWidth: 700,
        width: "100%",
        mx: "auto",
        backgroundColor: "#f5f5f7",
        color: "#111",
        borderRadius: 3,
        padding: 2,
        boxShadow: "0 6px 25px rgba(0,0,0,0.15)",
        transition: "all 0.3s ease",
        "&:hover": {
          boxShadow: "0 12px 35px rgba(0,150,255,0.25)",
          transform: "translateY(-4px)",
        },
      }}
    >
      <CardContent sx={{ p: 2 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          {/* Left: Text Info */}
          <Box sx={{ flex: 1 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1, fontSize: "1.1rem" }}>
              Detection Result
            </Typography>

            <Typography sx={{ mb: 1, fontSize: "0.95rem" }}>
              <strong>Item Type:</strong> {result.item_type}
            </Typography>

            <Typography sx={{ mb: 1, fontSize: "0.95rem" }}>
              <strong>Model Count:</strong> {result.model_count}
            </Typography>

            <Typography sx={{ mb: 1, fontSize: "0.95rem" }}>
              <strong>User Correction:</strong> {result.user_correction || "None"}
            </Typography>

            <Button
              variant="contained"
              onClick={() => navigate("/detection-result", { state: { result } })}
              sx={{
                mt: 1,
                fontWeight: 600,
                background: "linear-gradient(135deg,#2e7d32,#1b5e20)",
                px: 2,
                py: 0.5,
                fontSize: "0.85rem",
                borderRadius: 2,
                boxShadow: "0 3px 10px rgba(46,125,50,0.4)",
                transition: "all 0.3s ease",
                "&:hover": {
                  boxShadow: "0 6px 15px rgba(46,125,50,0.5)",
                  transform: "translateY(-2px)",
                },
              }}
            >
              Submit Correction
            </Button>
          </Box>

          {/* Right: Image */}
          {result.image_path && (
            <Box
              sx={{
                width: 120,
                height: 120,
                flexShrink: 0,
                borderRadius: 2,
                overflow: "hidden",
                boxShadow: "0 3px 8px rgba(0,0,0,0.15)",
              }}
            >
              <img
                src={`http://localhost:5000/${result.image_path}`} // Adjust based on your backend setup
                alt="Result"
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit: "cover", // ensures uniform size
                }}
              />
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  ))}
</Box>
</Box>
  );
};

export default ResultsPage;
