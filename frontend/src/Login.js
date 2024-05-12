import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import SendIcon from "@mui/icons-material/Send";

import React, { useState, useEffect } from "react";

function Login() {
  const [authenticated, setSetAuthenticated] = useState(false);

  const getAuthenticated = async () => {
    const res = await fetch("/login");
    const data = await res.json();
    setSetAuthenticated(data.authenticated);
  };
  useEffect(() => {
    getAuthenticated();
  });

  return (
    <div>
      <Box
        display="flex"
        justifyContent="center"
        alignItems="top"
        minHeight="100vh"
        component="form"
        sx={{
          "& > :not(style)": { m: 1, width: "20ch" },
        }}
        noValidate
        autoComplete="on"
      >
        <TextField id="outlined-basic" label="Username" variant="outlined" />
        <TextField id="outlined-basic" label="Password" variant="outlined" />
        <Button
          endIcon={<SendIcon />}
          onClick={() => {
            fetch("/login");
          }}
        >
          Login
        </Button>
      </Box>
    </div>
  );
}

export default Login;
