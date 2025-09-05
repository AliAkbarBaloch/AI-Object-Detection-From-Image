import { useState } from "react";
import { correctResult } from "../api/imageApi";
import { Card, CardContent, Typography, TextField, Button, Box } from "@mui/material";
import { useSnackbar } from "notistack";
import { useLocation, useNavigate } from "react-router-dom";


const DetectionResult = ({ result }) => {
  const [correctCounts, setCorrectCounts] = useState({});
  const [userCorrections, setUserCorrections] = useState({});
  const { enqueueSnackbar } = useSnackbar();
  const navigate = useNavigate();
  const location = useLocation();
  const dat = location.state?.result || result;

  // Pagination state
  const resultsArray = dat?.results || [dat];
  const [page, setPage] = useState(1);
  const perPage = 1;
  const pageCount = Math.ceil(resultsArray.length / perPage);
  const paginatedResults = resultsArray.slice((page - 1) * perPage, page * perPage);
  if (!dat) return null;

  const handleCorrection = async (result_id) => {
    const correctCount = correctCounts[result_id];
    if (correctCount === undefined || correctCount === "") {
      enqueueSnackbar("Please enter a correct count", { variant: "warning" });
      return;
    }
    try {
      await correctResult({ result_id, correct_count: correctCount });
      setUserCorrections((prev) => ({ ...prev, [result_id]: correctCount }));
      enqueueSnackbar("Correction saved", { variant: "success" });
    } catch (err) {
      enqueueSnackbar(err?.response?.data?.error || "Correction failed", { variant: "error" });
    }
  };

  return (
    <Box sx={{ position:'fixed', inset:0, width: '100%', height: '100vh', overflow: 'hidden', display: 'flex', justifyContent: 'center', alignItems:'center', bgcolor:'#fafafa' }}>
      <Box sx={{ width: '100%', maxWidth: { xs: 380, sm: 760, md: 1200 }, mx: 'auto', display: 'flex', flexDirection: 'column', alignItems: 'center', p: { xs: 1, sm: 1.5, md: 2 }, height: '100%' }}>
        <Box sx={{ width: '100%', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        {paginatedResults.map((res, idx) => {
          const globalIdx = (page - 1) * perPage + idx;
          const imsage_src = res.image_url ? res.image_url : (res.image_path ? `http://localhost:5000/${res.image_path}` : null);
          const segmentation_src = res.segmentation_url ? res.segmentation_url : (res.segmentation_image_path ? `http://localhost:5000/${res.segmentation_image_path}` : null);
          const merged_matches_src = res.matched_segments_merged_url
            ? res.matched_segments_merged_url
            : (res.matched_segments_merged_path ? `http://localhost:5000/${res.matched_segments_merged_path}` : null);
          // Normalize matched segments from various shapes: matched_segments (with filename/path/url), matched_segment_urls, matched_segment_image_paths
          const normalizedMatches = (() => {
            const items = [];
            if (Array.isArray(res.matched_segments) && res.matched_segments.length) {
              for (const m of res.matched_segments) {
                const url = m.url || (m.path ? `http://localhost:5000/${m.path}` : (m.filename ? `http://localhost:5000/uploads/${m.filename}` : null));
                if (url) items.push({ url, label: m.label || 'N/A', predicted_class: m.predicted_class || 'N/A' });
              }
            }
            if (!items.length && Array.isArray(res.matched_segment_urls)) {
              for (const u of res.matched_segment_urls) items.push({ url: u, label: 'N/A', predicted_class: 'N/A' });
            }
            if (!items.length && Array.isArray(res.matched_segment_image_paths)) {
              for (const p of res.matched_segment_image_paths) items.push({ url: `http://localhost:5000/${p}`, label: 'N/A', predicted_class: 'N/A' });
            }
            return items;
          })();
          const conter = res.count !== undefined ? res.count : res.model_count;
          const userCorrection = userCorrections[res.result_id] !== undefined ? userCorrections[res.result_id] : (res.user_correction !== undefined ? res.user_correction : 0);
          return (
            <Card className="app-card" key={res.result_id || globalIdx} sx={{
              width: '100%',
              maxHeight: '90vh',
              mx: 'auto',
              background: '#fff',
              color: '#111',
              borderRadius: 6,
              p: { xs: 1.5, sm: 2, md: 3 },
              boxShadow: '0 8px 40px rgba(0,0,0,0.10)',
              transition: 'all 0.3s ease',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'flex-start',
              overflow:'hidden',
              '&:hover': { boxShadow: '0 16px 60px rgba(0,150,255,0.15)' },
            }}>
              <CardContent sx={{ width: "100%", display: "flex", flexDirection: "column", alignItems: "center", p: 0, flexGrow: 1 }}>
                <Typography variant="h5" sx={{ fontWeight: 900, mb: { xs: 0.75, sm: 1.25 }, color: "#1976d2", letterSpacing: 1, fontSize: { xs: "1.2rem", sm: "1.5rem" } }}>
                  Detection Result {resultsArray.length > 1 ? `#${globalIdx + 1}` : ""}
                </Typography>
                {(segmentation_src || imsage_src) && (
                  <Box sx={{ display: 'flex', gap: 1.5, width: '100%', mb: { xs: 1.5, sm: 2 }, alignItems: 'stretch', flexGrow:0 }}>
                    <Box
                      sx={{
                        flex: 3,
                        height: { xs: '26vh', sm: '34vh' },
                        background: "#f5f5f7",
                        borderRadius: "12px",
                        boxShadow: "0 4px 18px rgba(25,118,210,0.10)",
                        overflow: "hidden",
                      }}
                    >
                      <img
                        src={segmentation_src || imsage_src}
                        alt={segmentation_src ? "Segmentation" : "Original"}
                        style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                      />
                    </Box>
                    {/* Right rail: either merged composite or grid of segments with captions */}
                    {merged_matches_src ? (
                      <Box sx={{ flex: 2, height: { xs: '26vh', sm: '34vh' }, background: '#f5f5f7', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 2px 8px rgba(0,0,0,0.10)' }}>
                        <img src={merged_matches_src} alt="Matched Segments" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                      </Box>
                    ) : normalizedMatches.length > 0 ? (
                      <Box sx={{ flex: 2, display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)' }, gap: 1, maxHeight: { xs: '26vh', sm: '34vh' }, overflow: 'hidden' }}>
            {normalizedMatches.map((m, i) => (
                          <Box key={i} sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                            <Box sx={{ width: '100%', aspectRatio: '1 / 1', borderRadius: '10px', overflow: 'hidden', background: '#f5f5f7', boxShadow: '0 2px 8px rgba(0,0,0,0.10)' }}>
                <img src={m.url} alt={`Match ${i + 1}`} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                            </Box>
                            <Typography variant="caption" sx={{ color: '#444', fontWeight: 700 }}>
                              Predicted_Class: {m.predicted_class} | Label: {m.label}
                            </Typography>
                          </Box>
                        ))}
                      </Box>
                    ) : null}
                  </Box>
                )}
                <Typography sx={{ mb: { xs: 0.75, sm: 1 }, fontSize: { xs: "1rem", sm: "1.1rem" }, color: "#333" }}>
                  <strong>Model Count:</strong> {conter}
                </Typography>
                <Typography sx={{ mb: { xs: 0.75, sm: 1.25 }, fontSize: { xs: "1rem", sm: "1.1rem" }, color: "#333" }}>
                  <strong>User Correction:</strong> {userCorrection}
                </Typography>
                <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1.5, width: "100%" }}>
                  <TextField
                    label="Correct Count"
                    type="number"
                    value={correctCounts[res.result_id] || ""}
                    onChange={(e) => setCorrectCounts({ ...correctCounts, [res.result_id]: e.target.value })}
                    fullWidth
                  />
                  <Button
                    variant="contained"
                    onClick={() => handleCorrection(res.result_id)}
                    fullWidth
                    sx={{
                      py: { xs: 0.9, sm: 1.2 },
                      fontWeight: 800,
                      fontSize: { xs: "1rem", sm: "1.1rem" },
                      background: "linear-gradient(135deg,#2e7d32,#1b5e20)",
                      color: "#fff",
                      borderRadius: 3,
                      boxShadow: "0 3px 10px rgba(46,125,50,0.15)",
                      transition: "all 0.3s ease",
                      '&:hover': {
                        boxShadow: "0 6px 15px rgba(46,125,50,0.25)",
                        transform: "translateY(-2px)",
                      },
                    }}
                  >
                    Submit Correction
                  </Button>
                </Box>
                {/* Spacer to push footer actions to the bottom for stable height */}
                {/* Removed extra flex spacer to fit within viewport */}
                <Box sx={{ display: "flex", justifyContent: "flex-end", mt: { xs: 1, sm: 1.5 }, width: "100%" }}>
                  <Button
                    variant="outlined"
                    color="primary"
                    onClick={() => navigate("/results")}
                    fullWidth
                    sx={{ fontWeight: 800, py: { xs: 0.9, sm: 1.2 }, minWidth: 120, borderRadius: 3, borderColor: "#1976d2", color: "#1976d2", fontSize: { xs: "1rem", sm: "1.1rem" } }}
                  >
                    Previous Results
                  </Button>
                </Box>
              </CardContent>
            </Card>
          );
        })}
  {/* Pagination controls (kept but will not cause scroll) */}
  {pageCount > 1 && (
          <Box sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            mt: "-4px",
            gap: 1,
            background: "#f5f5f7",
            borderRadius: 3,
            boxShadow: "0 4px 15px rgba(0,0,0,0.10)",
            px: { xs: 0.75, sm: 1 },
            pt: "4px",
            pb: { xs: 0.5, sm: 0.75 },
            color: "#111",
            width: "auto",
            mx: "auto",
          }}>
            <Button
              variant="text"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              sx={{ fontWeight: 700, minWidth: { xs: 64, sm: 80 }, px: 1.5, py: 0.6, border: 'none', boxShadow: 'none' }}
            >
              Previous
            </Button>
            <Typography sx={{ alignSelf: "center", fontWeight: 700, mx: 1, color: "#1976d2", fontSize: { xs: "0.95rem", sm: "1rem" } }}>
              Page {page} of {pageCount}
            </Typography>
            <Button
              variant="text"
              onClick={() => setPage((p) => Math.min(pageCount, p + 1))}
              disabled={page === pageCount}
              sx={{ fontWeight: 700, minWidth: { xs: 64, sm: 80 }, px: 1.5, py: 0.6, border: 'none', boxShadow: 'none' }}
            >
              Next
            </Button>
          </Box>
        )}
        </Box>
      </Box>
    </Box>
  );
};

export default DetectionResult;
