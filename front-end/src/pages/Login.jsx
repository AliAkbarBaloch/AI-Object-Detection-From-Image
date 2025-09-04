import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Card,
  CardContent,
  Button,
  Typography,
  Box,
  TextField,
} from "@mui/material";
import { useSnackbar } from "notistack";
import '../styles/global.css';
import { loginUser } from "../api/imageApi";

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {

    e.preventDefault();

    setLoading(true);

    try {

      const data = await loginUser(email, password);

      // Store the authentication token (adjust based on your API response)

      if (data.token) {

        localStorage.setItem('authToken', data.token);

        localStorage.setItem('user', JSON.stringify(data.user));

      }

      enqueueSnackbar("Login successful!", { variant: "success" });

      navigate('/results');

    } catch (err) {

      enqueueSnackbar(err?.response?.data?.error || "Login failed", {

        variant: "error",

      });

    } finally {

      setLoading(false);

    }

  };

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
        padding: 2,
      }}
    >
      <Card
        sx={{
          maxWidth: 500,
          width: "100%",
          mx: "auto",
          backgroundColor: "#f5f5f7",
          color: "#111",
          borderRadius: 4,
          padding: 5,
          boxShadow: "0 14px 60px rgba(0,0,0,0.25)",
          transition: "all 0.3s ease",
          "&:hover": {
            boxShadow: "0 20px 70px rgba(0,150,255,0.2)",
            transform: "translateY(-6px)",
          },
        }}
      >
        <CardContent>
          <Typography 
            variant="h5" 
            sx={{ 
              fontWeight: 700, 
              mb: 2, 
              textAlign: "center" 
            }}
          >
            Login to Your Account
          </Typography>
          <Typography 
            variant="body2" 
            sx={{ 
              color: "#555", 
              mb: 4, 
              textAlign: "center" 
            }}
          >
            Enter your credentials to access your account
          </Typography>

          <form onSubmit={handleSubmit}>
            <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
              {/* Email Field */}
              <TextField
                type="email"
                label="Email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
                sx={{
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
                }}
              />

              {/* Password Field */}
              <TextField
                type="password"
                label="Password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
                sx={{
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
                }}
              />

              {/* Submit Button */}
              <Button
                type="submit"
                variant="contained"
                fullWidth
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
                {loading ? "Logging in..." : "Login"}
              </Button>

              <Typography 
                variant="body2" 
                sx={{ 
                  textAlign: "center", 
                  mt: 2 
                }}
              >
                Don't have an account?{" "}
                <Link 
                  to="/register" 
                  style={{ 
                    color: "#1976d2", 
                    textDecoration: "none",
                    fontWeight: 600 
                  }}
                >
                  Register
                </Link>
              </Typography>
            </Box>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Login;