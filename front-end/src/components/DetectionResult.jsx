import { use, useState } from "react";
import { correctResult } from "../api/imageApi";
import { Card, CardContent, Typography, TextField, Button, Box } from "@mui/material";
import { useSnackbar } from "notistack";
import { useLocation, useNavigate } from "react-router-dom";

const DetectionResult = ({ result }) => {
  const [correctCount, setCorrectCount] = useState("");
  const { enqueueSnackbar } = useSnackbar();
  const navigate = useNavigate();
  const location = useLocation();
  const dat = location.state?.result;
  const imsage_src = dat.image_url ? dat.image_url: `http://localhost:5000/${dat.image_path}`;
  const conter = dat.count ? dat.count: dat.model_count;
    //console.log(dat +" asasd");
  if (!dat) return null;
  console.log(imsage_src +" asasd");
  //console.log(dat.model_count +" asasd");
  



  const handleCorrection = async () => {
    if (!correctCount) {
      enqueueSnackbar("Please enter a correct count", { variant: "warning" });
      return;
    }
    
    try {
      await correctResult({ result_id: dat.result_id, correct_count: correctCount });

      navigate("/results");
      enqueueSnackbar("Correction saved", { variant: "success" });
    } catch (err) {
      enqueueSnackbar(err?.response?.data?.error || "Correction failed", { variant: "error" });
    }
  };

  return (
    <Card className="app-card" sx={{
    maxWidth: 800, // slightly wider
    width: "100%",
    mx: "auto",
    backgroundColor: "#f5f5f7", // soft white
    color: "#111",
    borderRadius: 4, // 32px for premium feel
    padding: 5, // 40px padding
    boxShadow: "0 14px 60px rgba(0,0,0,0.25)", // soft shadow
    transition: "all 0.3s ease",
    "&:hover": {
      boxShadow: "0 20px 70px rgba(0,150,255,0.2)",
      transform: "translateY(-6px)",
    },
  }}>
      <CardContent>
        <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
          Detection Result
        </Typography>
        {/* Show the image */}
        {imsage_src && (
          <Box sx={{ display: "flex", justifyContent: "center", mb: 3 }}>
            <img
              src={imsage_src} // ✅ Full URL
              alt="Uploaded"
              style={{
                maxWidth: "100%",
                maxHeight: "300px",
                borderRadius: "8px",
                boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
              }}
            />
          </Box>
        )}
        <Typography sx={{ mb: 2 }}>
          <strong>Detected Count:</strong> {conter}
        </Typography>

        <Box sx={{ display: "flex", gap: 2, flexDirection: "column" }}>
          <TextField
            label="Correct Count"
            type="number"
            value={correctCount}
            onChange={(e) => setCorrectCount(e.target.value)}
            fullWidth
          />
          <Button
            variant="contained"
            onClick={handleCorrection}
            sx={{ py: 1.25, fontWeight: 700, background: "linear-gradient(135deg,#2e7d32,#1b5e20)",transition: "all 0.3s ease",
    "&:hover": {
      boxShadow: "0 8px 22px rgba(123, 31, 162, 0.35)",
      transform: "translateY(-2px)",
      opacity: 1,
    }, }}
          >
            Submit Correction
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default DetectionResult;
