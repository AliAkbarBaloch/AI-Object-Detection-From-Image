import React, { useEffect, useMemo, useState } from "react";
import { getPreviousResults } from "../api/imageApi"; // adjust path // your axios instance
import { useLocation, useNavigate } from "react-router-dom";
import { Card, CardContent, Typography, Box, Button } from "@mui/material";


const ResultsPage = () => {
  const [results, setResults] = useState([]);
  const [page, setPage] = useState(1);
  const perPage = 1; // show one card per page
  const pageCount = Math.ceil(results.length / perPage);
  const paginatedResults = results.slice((page - 1) * perPage, page * perPage);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchResults = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getPreviousResults();
        // If data is an array, use it. If it's an object, try to extract array property.
        if (Array.isArray(data)) {
          setResults(data);
        } else if (data && Array.isArray(data.results)) {
          setResults(data.results);
        } else {
          setResults([]);
        }
      } catch (err) {
        setError("Failed to fetch results");
        setResults([]);
      } finally {
        setLoading(false);
      }
    };
    fetchResults();
  }, []);

  return (
    <Box sx={{
      position: 'fixed',
      inset: 0,
      width: '100%',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'flex-start',
      overflow: 'hidden',
      pt: { xs: 4, sm: 5 }, // push content a bit lower from the very top
      pb: { xs: 1, sm: 2 },
      px: 0,
      bgcolor: '#fafafa'
    }}>
    <Box
        sx={{
      width: "100%",
      maxWidth: { xs: 360, sm: 720, md: 1000 },
          mx: "auto",
          mb: 2,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          px: 2,
        }}
      >
        <Typography
          variant="h4"
          sx={{
            fontWeight: 800,
            color: "#1976d2",
            textShadow: "0 2px 8px rgba(25,118,210,0.08)",
            letterSpacing: 1,
          }}
        >
          Previous Results
        </Typography>
        <Button
          variant="contained"
          onClick={() => navigate("/home")}
          sx={{
            ml: 3,
            background: "linear-gradient(135deg,#1976d2,#0d47a1)",
            fontWeight: 700,
            px: 3,
            py: 1.5,
            borderRadius: 2,
            transition: "all 0.3s ease",
            boxShadow: "0 4px 15px rgba(25, 118, 210, 0.3)",
            '&:hover': {
              boxShadow: "0 8px 22px rgba(25, 118, 210, 0.35)",
              transform: "translateY(-2px)",
            },
          }}
        >
          Home
        </Button>
      </Box>
      {loading ? (
        <Typography align="center" sx={{ mt: 8, color: '#888' }}>Loading...</Typography>
      ) : error ? (
        <Typography align="center" sx={{ mt: 8, color: 'red' }}>{error}</Typography>
      ) : (
        <>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, width: "100%", maxWidth: { xs: 360, sm: 720, md: 1000 }, mx: "auto" }}>
            {paginatedResults.map((result) => (
              <Card
                key={result._id}
                sx={{
                  width: "100%",
                  mx: "auto",
                  background: "#fff",
                  color: "#111",
                  borderRadius: 6,
                  padding: { xs: 1.5, sm: 2 },
                  boxShadow: "0 8px 40px rgba(0,0,0,0.10)",
                  transition: "all 0.3s ease",
                  '&:hover': {
                    boxShadow: "0 16px 60px rgba(0,150,255,0.15)",
                    transform: "translateY(-4px)",
                  },
                }}
              >
                <CardContent sx={{ p: 1.5, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  {/* Images row */}
                  {(result.segmentation_image_path || result.image_path) && (
                    <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'stretch', width: '100%', justifyContent: 'center', mb: { xs: 2, sm: 2.5 }, maxHeight: { xs: '50vh', sm: '52vh' } }}>
                      <Box
                        sx={{
                          flex: 1,
                          maxWidth: { xs: 240, sm: 320, md: 380 },
                          height: { xs: '32vh', sm: '34vh', md: '38vh' },
                          borderRadius: 3,
                          overflow: 'hidden',
                          boxShadow: '0 3px 8px rgba(0,0,0,0.10)',
                          background: '#f5f5f7',
                        }}
                      >
                        <img
                          src={`http://localhost:5000/${result.segmentation_image_path || result.image_path}`}
                          alt="Segmentation"
                          style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                        />
                      </Box>
                      {(() => {
                        const mergedDispUrl = result.matched_segments_merged_url
                          || (result.matched_segments_merged_path ? `http://localhost:5000/${result.matched_segments_merged_path}` : null);
                        if (mergedDispUrl) {
                          return (
                            <Box sx={{ flex: 1, maxWidth: { xs: 240, sm: 320, md: 380 }, height: { xs: '32vh', sm: '34vh', md: '38vh' }, borderRadius: 3, overflow: 'hidden', boxShadow: '0 3px 8px rgba(0,0,0,0.10)', background: '#f5f5f7' }}>
                              <img src={mergedDispUrl} alt="Matched Segments" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                            </Box>
                          );
                        }
                        const listMatches = Array.isArray(result.matched_segments) && result.matched_segments.length
                          ? result.matched_segments
                          : (Array.isArray(result.matched_segment_image_paths) ? result.matched_segment_image_paths.map((p) => ({ path: p, url: `http://localhost:5000/${p}`, label: 'N/A', predicted_class: 'N/A' })) : []);
                        return listMatches.length > 0 ? (
                          <Box sx={{ flex: 1, maxWidth: { xs: 240, sm: 320, md: 380 }, height: { xs: '32vh', sm: '34vh', md: '38vh' }, display: 'flex' }}>
                            <ThumbnailsWithCaptions items={listMatches} cardKey={result._id} />
                          </Box>
                        ) : null;
                      })()}
                    </Box>
                  )}
                  {/* Text info & button below images */}
                  <Box sx={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <Box
                      sx={{
                        display: 'flex',
                        flexWrap: 'wrap',
                        gap: { xs: 1.5, sm: 3 },
                        alignItems: 'center',
                        justifyContent: 'center',
                        mb: 2,
                        fontSize: { xs: '0.95rem', sm: '1.05rem' },
                        textAlign: 'center',
                      }}
                    >
                      <Typography sx={{ fontSize: 'inherit', textAlign: 'center' }}><strong>Item Type:</strong> {result.item_type}</Typography>
                      <Typography sx={{ fontSize: 'inherit', textAlign: 'center' }}><strong>Model Count:</strong> {result.model_count}</Typography>
                      <Typography sx={{ fontSize: 'inherit', textAlign: 'center' }}><strong>User Correction:</strong> {result.user_correction || 'None'}</Typography>
                    </Box>
                    <Button
                      variant="contained"
                      onClick={() => {
                        const segUrl = result.segmentation_image_path
                          ? `http://localhost:5000/${result.segmentation_image_path}`
                          : (result.image_path ? `http://localhost:5000/${result.image_path}` : null);
                        const mergedUrl = result.matched_segments_merged_url
                          || (result.matched_segments_merged_path ? `http://localhost:5000/${result.matched_segments_merged_path}` : null);
                        const normalizedMatches = (() => {
                          if (Array.isArray(result.matched_segments) && result.matched_segments.length) {
                            return result.matched_segments.map((m) => ({
                              url: m.url || (m.path ? `http://localhost:5000/${m.path}` : (m.filename ? `http://localhost:5000/uploads/${m.filename}` : '')),
                              label: m.label || 'N/A',
                              predicted_class: m.predicted_class || 'N/A',
                              path: m.path || (m.filename ? `uploads/${m.filename}` : undefined),
                            })).filter(x => !!x.url);
                          }
                          if (Array.isArray(result.matched_segment_image_paths) && result.matched_segment_image_paths.length) {
                            return result.matched_segment_image_paths.map((p) => ({ url: `http://localhost:5000/${p}`, label: 'N/A', predicted_class: 'N/A', path: p }));
                          }
                          if (Array.isArray(result.matched_segment_urls) && result.matched_segment_urls.length) {
                            return result.matched_segment_urls.map((u) => ({ url: u, label: 'N/A', predicted_class: 'N/A' }));
                          }
                          return [];
                        })();
                        const enriched = { ...result, segmentation_url: segUrl, matched_segments: normalizedMatches, matched_segments_merged_url: mergedUrl };
                        navigate('/detection-result', { state: { result: enriched } });
                      }}
                      sx={{
                        alignSelf: 'stretch',
                        fontWeight: 700,
                        background: 'linear-gradient(135deg,#2e7d32,#1b5e20)',
                        px: 2.5,
                        py: 1.2,
                        fontSize: '1rem',
                        borderRadius: 2,
                        boxShadow: '0 3px 10px rgba(46,125,50,0.2)',
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          boxShadow: '0 6px 15px rgba(46,125,50,0.3)',
                          transform: 'translateY(-2px)',
                        },
                      }}
                    >
                      Submit Correction
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Box>
          {/* Pagination controls */}
          {pageCount > 1 && (
            <Box sx={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              mt: { xs: 0.5, sm: 1 },
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
        </>
      )}
    </Box>
  );
};

export default ResultsPage;

// Local helper to render thumbnails with a stable pseudo-random selection when many
function ThumbnailsWithCaptions({ items, cardKey }) {
  const maxThumbs = 6;
  const minThumbs = 3;
  const selected = useStableSample(items, Math.max(minThumbs, Math.min(maxThumbs, items.length)), cardKey);
  return (
    <Box sx={{
      display: 'grid',
      gridTemplateColumns: { xs: 'repeat(2, 1fr)', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' },
      gap: 1,
      width: { xs: 180, sm: 240, md: 300 },
      alignContent: 'start',
    }}>
      {selected.map((m, i) => (
        <Box key={`${cardKey}-${i}`} sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
          <Typography variant="caption" sx={{ color: '#000', fontWeight: 700 }}>
            Predicted_Class: {m.predicted_class} | Label: {m.label}
          </Typography>
          <Box sx={{ width: '100%', aspectRatio: '1 / 1', borderRadius: 2, overflow: 'hidden', background: '#f5f5f7', boxShadow: '0 2px 6px rgba(0,0,0,0.08)' }}>
            <img src={m.url || (m.path ? `http://localhost:5000/${m.path}` : '')} alt={`Match ${i + 1}`} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          </Box>
        </Box>
      ))}
    </Box>
  );
}

function useStableSample(items, count, seedStr) {
  return useMemo(() => {
    if (!Array.isArray(items) || items.length === 0) return [];
    const seed = stableHash(seedStr || '') % 2147483647;
  const arr = [...items];
    // Fisher-Yates with seeded RNG
    let rngState = seed || 1;
    const rand = () => (rngState = (rngState * 48271) % 2147483647) / 2147483647;
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(rand() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr.slice(0, Math.min(count, arr.length));
  }, [items, count, seedStr]);
}

function stableHash(str) {
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h += (h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24);
  }
  return Math.abs(h | 0);
}
