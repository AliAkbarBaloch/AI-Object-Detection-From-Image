import CircularProgress from "@mui/material/CircularProgress";
import Box from "@mui/material/Box";

const Loader = () => (
  <Box sx={{ display: "flex", justifyContent: "center", mt: 3 }}>
    <CircularProgress />
  </Box>
);

export default Loader;
