import React, { Fragment, useState, useEffect } from "react";

import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Button from "@mui/material/Button";
import DeleteIcon from "@mui/icons-material/Delete";
import SendIcon from "@mui/icons-material/Send";
import Box from "@mui/material/Box";
import FormControl from "@mui/material/FormControl";

function App() {
  const [clusterPools, setClusterPools] = useState([]);
  const [clusterClaims, setClusterClaims] = useState([]);
  const [loading, setLoading] = useState(false);
  const [deleteClaim, setDeleteClaim] = React.useState("");
  const [claimsCreds, setClaimCreds] = React.useState([]);

  const handleChangeDeleteClaim = (event) => {
    setDeleteClaim(event.target.value);
    console.log(deleteClaim);
  };

  const getClusterPools = async () => {
    setLoading(true);
    const res = await fetch("/cluster-pools");
    const data = await res.json();
    setClusterPools(data);
    console.log(data);
    setLoading(false);
  };

  const getClusterClaims = async () => {
    setLoading(true);
    const res = await fetch("/cluster-claims");
    const data = await res.json();
    setClusterClaims(data);
    console.log(data.data);
    setLoading(false);
  };

  const getCliamCreds = async () => {
    setLoading(true);
    clusterClaims.data.forEach(async (claim) => {
      const res = await fetch("/cluster-creds/?name=" + claim.name);
      const data = await res.json();
      console.log(data);
      setClaimCreds((prev) => [...prev, data]);
    });
    setLoading(false);
  };

  useEffect(() => {
    getClusterPools();
    getClusterClaims();
  }, []);

  return (
    <Fragment>
      <h1>Hive Claim System</h1>
      <div className="main">
        <section className="section">
          <h3>Cluster Pools</h3>
          <div>
            {loading ? (
              <Fragment>loading...</Fragment>
            ) : (
              <Fragment>
                <TableContainer component={Paper}>
                  <Table
                    sx={{ minWidth: 350 }}
                    size="small"
                    aria-label="simple table"
                  >
                    <TableHead>
                      <TableRow>
                        <TableCell>Name</TableCell>
                        <TableCell align="center">Size</TableCell>
                        <TableCell align="center">Claimed</TableCell>
                        <TableCell align="center">Available</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {clusterPools.map((pool) => (
                        <TableRow
                          key={pool.name}
                          sx={{
                            "&:last-child td, &:last-child th": { border: 0 },
                          }}
                        >
                          <TableCell component="th" scope="row">
                            {pool.name}
                          </TableCell>
                          <TableCell align="center">{pool.size}</TableCell>
                          <TableCell align="center">{pool.claimed}</TableCell>
                          <TableCell align="center">{pool.available}</TableCell>
                          <TableCell align="center">
                            <Button endIcon={<SendIcon />}>Claim</Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Fragment>
            )}
          </div>
        </section>

        <section className="section">
          <h3>Active Claims</h3>
          <div>
            {loading ? (
              <Fragment>loading...</Fragment>
            ) : (
              <Fragment>
                <TableContainer component={Paper}>
                  <Table
                    sx={{ minWidth: 350 }}
                    size="small"
                    aria-label="simple table"
                  >
                    <TableHead>
                      <TableRow>
                        <TableCell>Name</TableCell>
                        <TableCell align="center">Poll</TableCell>
                        <TableCell align="center">Namespace</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {clusterClaims.map((claim) => (
                        <TableRow
                          key={claim.name}
                          sx={{
                            "&:last-child td, &:last-child th": { border: 0 },
                          }}
                        >
                          <TableCell component="th" scope="row">
                            {claim.name}
                          </TableCell>
                          <TableCell align="center">{claim.pool}</TableCell>
                          <TableCell align="center">
                            {claim.namespace}
                          </TableCell>
                          <TableCell align="center">
                            <Button endIcon={<SendIcon />}>View</Button>
                          </TableCell>
                          <TableCell align="center">
                            <Button
                              color="error"
                              startIcon={<DeleteIcon />}
                              onClick={() => {
                                alert(claim.name + ": clicked");
                              }}
                            >
                              {" "}
                              Delete{" "}
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Fragment>
            )}
          </div>
        </section>

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
      </div>
    </Fragment>
  );
}

export default App;
