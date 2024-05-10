import React, { useState, useEffect } from "react";

import Stack from "@mui/material/Stack";
import Button from "@mui/material/Button";
import DeleteIcon from "@mui/icons-material/Delete";
import Box from "@mui/material/Box";
import FormControl from "@mui/material/FormControl";

function DeleteAllClaims() {
  const [clusterClaims, setClusterClaims] = useState([]);
  const [loading, setLoading] = useState(false);

  const getClusterClaims = async () => {
    setLoading(true);
    const res = await fetch("/cluster-claims");
    const data = await res.json();
    setClusterClaims(data);
    setLoading(false);
  };

  useEffect(() => {
    getClusterClaims();
  }, []);

  return (
    <div>
      {loading ? (
        <>loading...</>
      ) : (
        <Box sx={{ minWidth: 120 }}>
          <FormControl fullWidth>
            <Stack direction="row" spacing={2}>
              <Button
                color="error"
                startIcon={<DeleteIcon />}
                onClick={() => {
                  alert(clusterClaims.map((claim) => claim.name) + ": clicked");
                }}
              >
                {" "}
                Delete All Claims{" "}
              </Button>
            </Stack>
          </FormControl>
        </Box>
      )}
    </div>
  );
}

export default DeleteAllClaims;
