
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import DetectionResult from "./components/DetectionResult";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ResultsPage from "./pages/ResultList";


const AppRoutes = () => (
  <Router>
    <Routes>
      <Route path="/home" element={<Home />} />
      <Route path="/results" element={<ResultsPage />} />
      <Route path="/detection-result" element={<DetectionResult />} />
      <Route path="/" element={<Login />} />
      <Route path="/register" element={<Register />} />
    </Routes>
  </Router>
);

export default AppRoutes;
