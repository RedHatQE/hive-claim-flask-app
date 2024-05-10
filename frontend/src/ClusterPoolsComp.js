import React, { useState, useEffect } from "react";

import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";
import Button from "@mui/material/Button";
import SendIcon from "@mui/icons-material/Send";

function ClusterPools() {
  const [clusterPools, setClusterPools] = useState([]);
  const [loading, setLoading] = useState(false);

  const getClusterPools = async () => {
    setLoading(true);
    const res = await fetch("/cluster-pools");
    const data = await res.json();
    setClusterPools(data);
    setLoading(false);
  };

  useEffect(() => {
    getClusterPools();
  }, []);

  return (
    <section className="section">
      <h3>Cluster Pools</h3>
      <div>
        {loading ? (
          <>loading...</>
        ) : (
          <>
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
                        <Button
                          endIcon={<SendIcon />}
                          onClick={() => {
                            fetch("/claim-cluster?name=" + pool.name);
                          }}
                        >
                          Claim
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </>
        )}
      </div>
    </section>
  );
}

export default ClusterPools;
