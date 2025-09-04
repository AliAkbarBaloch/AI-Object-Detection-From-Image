import { useState } from "react";
import { uploadImage } from "../api/imageApi";
import {
  Card,
  CardContent,
  Button,
  Typography,
  Box,
  TextField,
  Autocomplete,
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";

import Loader from "./Loader";
import { useSnackbar } from "notistack";
import { useNavigate } from "react-router-dom";

const options = [
  "car",
  "cat",
  "tree",
  "dog",
  "building",
  "person",
  "sky",
  "ground",
  "hardware",
];

const ImageUpload = ({ setResult }) => {
  const [file, setFile] = useState(null);
  const [itemType, setItemType] = useState("");
  const [loading, setLoading] = useState(false);
  const { enqueueSnackbar } = useSnackbar();
  const [currentResultId, setCurrentResultId] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !itemType) {
      enqueueSnackbar("Please select an image and item type", {
        variant: "warning",
      });
      return;
    }
    try {
      setLoading(true);
      const data = await uploadImage(file, itemType);
      setResult(data);
      navigate("/detection-result", { state: { result: data } });
      enqueueSnackbar("Image uploaded successfully!", { variant: "success" });
    } catch (err) {
      enqueueSnackbar(err?.response?.data?.error || "Upload failed", {
        variant: "error",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
  <Card
  sx={{
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
  }}
>
  <CardContent>
    <Typography variant="h5" sx={{ fontWeight: 700, mb: 2 }}>
      Upload an Image for Detection
    </Typography>
    <Typography variant="body2" sx={{ color: "#555", mb: 4 }}>
      Choose an image and the item type to get a detected count from the model.
    </Typography>

    <form onSubmit={handleSubmit}>
      <Box sx={{ display: "flex", flexDirection: "column", gap: 4 }}>
        {/* File Upload */}
        <Box>
          <Button
            variant="contained"
            component="label"
            fullWidth
            startIcon={<CloudUploadIcon />}
            sx={{
              py: 1.8,
              fontWeight: 700,
              background: "linear-gradient(135deg,#7b1fa2,#512da8)",
              transition: "all 0.3s ease",
              "&:hover": {
                boxShadow: "0 10px 28px rgba(123, 31, 162, 0.35)",
                transform: "translateY(-2px)",
              },
            }}
          >
            Choose Image
            <input
              type="file"
              accept="image/*"
              hidden
              onChange={(e) => setFile(e.target.files[0])}
            />
          </Button>

          {file && (
            <Typography sx={{ mt: 1, color: "#333", fontWeight: 600 }}>
              {file.name}
            </Typography>
          )}
        </Box>

        {/* Scrollable Autocomplete */}
        <Autocomplete
          sx={{
            width: "100%",
            "& .MuiOutlinedInput-root": {
              background: "#f9f9f9",
              borderRadius: 2,
              "& fieldset": { borderColor: "#ccc" },
              "&:hover fieldset": { borderColor: "#21cbf3" },
              "&.Mui-focused fieldset": {
                borderColor: "#21cbf3",
                boxShadow: "0 0 8px rgba(33, 203, 243, 0.3)",
              },
            },
            "& .MuiAutocomplete-popupIndicator": { color: "#21cbf3" },
          }}
          options={options}
          value={itemType || null}
          onChange={(e, newValue) => setItemType(newValue || "")}
          ListboxProps={{
            style: {
              maxHeight: 140, // scrollable
              overflowY: "auto",
              marginTop: 10, // space between input and list
            },
          }}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Select Item Type"
              placeholder="Choose one..."
              required
            />
          )}
        />

        {/* Submit Button */}
        <Button
          type="submit"
          variant="contained"
          fullWidth
          disabled={loading}
          sx={{
            py: 1.8,
            background: "linear-gradient(135deg,#1976d2,#21cbf3)",
            boxShadow: "0 8px 22px rgba(33,203,243,0.3)",
            transition: "all 0.3s ease",
            "&:hover": {
              boxShadow: "0 12px 30px rgba(33,203,243,0.5)",
              transform: "translateY(-2px)",
            },
          }}
        >
          {loading ? "Processing..." : "Upload & Detect"}
        </Button>

        {loading && <Loader />}
      </Box>
    </form>
  </CardContent>
</Card>


  );
};

export default ImageUpload;
