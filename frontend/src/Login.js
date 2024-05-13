import React, { useState } from "react";
import httpClient from "./httpClient";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import SendIcon from "@mui/icons-material/Send";
import Button from "@mui/material/Button";

const Login = () => {
  const [name, setUser] = useState("");
  const [password, setPassword] = useState("");

  const logInUser = async () => {
    try {
      await httpClient.post("//localhost:5000/login", {
        name,
        password,
      });

      window.location.href = "/";
    } catch (error) {
      if (error.response.status === 401) {
        alert("Invalid credentials");
      }
    }
  };

  return (
    <div>
      <h1 align="center">Log Into Your Account</h1>
      <Box
        component="form"
        sx={{
          "& .MuiTextField-root": { m: 1, width: "20ch" },
        }}
        noValidate
        autoComplete="off"
        display="flex"
        justifyContent="center"
        alignItems="top"
        minHeight="100vh"
      >
        <div>
          <TextField
            id="name"
            label="Username"
            defaultValue=""
            onChange={(e) => setUser(e.target.value)}
          />

          <TextField
            id="outlined-password-input"
            label="Password"
            type="password"
            autoComplete="current-password"
            onChange={(e) => setPassword(e.target.value)}
          />
          <Button
            variant="contained"
            endIcon={<SendIcon />}
            onClick={() => logInUser()}
          >
            {" "}
            Login{" "}
          </Button>
        </div>
      </Box>
    </div>
  );
};

export default Login;
