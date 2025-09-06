import { useState } from "react";
import { uploadImage, uploadImagesBatch } from "../api/imageApi";
import { Card, CardContent, Button, Typography, Box, TextField, Autocomplete, Chip } from "@mui/material";
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
  const [files, setFiles] = useState([]);
  const [itemType, setItemType] = useState("");
  const [loading, setLoading] = useState(false);
  const { enqueueSnackbar } = useSnackbar();
  const [currentResultId, setCurrentResultId] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!files.length || !itemType) {
      enqueueSnackbar("Please select at least one image and item type", {
        variant: "warning",
      });
      return;
    }
    try {
      setLoading(true);
      let data;
      if (files.length === 1) {
        data = await uploadImage(files[0], itemType);
        setResult(data);
        navigate("/detection-result", { state: { result: data } });
      } else {
        data = await uploadImagesBatch(files, itemType);
        setResult(data);
        navigate("/detection-result", { state: { result: data } });
      }
      enqueueSnackbar("Image(s) uploaded successfully!", { variant: "success" });
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
        maxWidth: 800,
        width: "100%",
        mx: "auto",
        backgroundColor: "#f5f5f7",
        color: "#111",
        borderRadius: 4,
        p: { xs: 2, sm: 3 },
        boxShadow: "0 14px 60px rgba(0,0,0,0.25)",
        transition: "all 0.3s ease",
        "&:hover": {
          boxShadow: "0 20px 70px rgba(0,150,255,0.2)",
          transform: "translateY(-6px)",
        },
      }}
    >
      <CardContent>
        <Typography variant="h5" sx={{ fontWeight: 700, mb: 1.5 }}>
          Upload an Image for Detection
        </Typography>
        <Typography variant="body2" sx={{ color: "#555", mb: 2 }}>
          Choose an image and the item type to get a detected count from the model.
        </Typography>

        <form onSubmit={handleSubmit}>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
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
              multiple
              onChange={(e) => setFiles(Array.from(e.target.files))}
            />
          </Button>

          {files && files.length > 0 && (
            <Box sx={{ mt: 1 }}>
              <Typography sx={{ color: "#333", fontWeight: 600 }}>
                {files.length === 1
                  ? "1 image selected:"
                  : `${files.length} images selected:`}
              </Typography>
              <Box
                sx={{
                  mt: 0.75,
                  maxHeight: 140,
                  overflowY: "auto",
                  display: "flex",
                  flexWrap: "wrap",
                  gap: 1,
                }}
              >
        {files.map((file, idx) => (
                  <Chip
          key={`${file.name}-${idx}`}
                    label={file.name}
                    size="small"
                    sx={{
                      bgcolor: "#eef2f7",
                      border: "1px solid #d0d7de",
                      color: "#333",
                    }}
                  />
                ))}
              </Box>
            </Box>
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

        {/* Submit and Previous Results Buttons */}
        <Box sx={{ display: "flex", flexDirection: "row", gap: 2, alignItems: "center" }}>
          <Button
            type="submit"
            variant="contained"
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
            fullWidth
          >
            {loading ? "Processing..." : "Upload & Detect"}
          </Button>
        </Box>
        <Box sx={{ display: "flex", justifyContent: "flex-end", mt: 2 }}>
          <Button
            variant="outlined"
            color="primary"
            onClick={() => navigate("/results")}
            fullWidth
            sx={{ fontWeight: 700, py: 1.4, minWidth: 160 }}
          >
            Previous Results
          </Button>
        </Box>

        {loading && <Loader />}
      </Box>
    </form>
  </CardContent>
</Card>


  );
};

export default ImageUpload;
