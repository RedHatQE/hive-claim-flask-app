import React, { useState, useEffect } from "react";

import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";
import Button from "@mui/material/Button";
import DeleteIcon from "@mui/icons-material/Delete";
import SendIcon from "@mui/icons-material/Send";
import Draggable from "react-draggable";

function ClusterClaims() {
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
    <section className="section">
      <h3>Active Claims</h3>
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
                      <TableCell align="center">{claim.namespace}</TableCell>
                      <TableCell align="center">
                        <Button
                          endIcon={<SendIcon />}
                          onClick={() => {
                            fetch("/cluster-creds?name=" + claim.name);
                          }}
                        >
                          View
                        </Button>
                      </TableCell>
                      <TableCell align="center">
                        <Button
                          color="error"
                          startIcon={<DeleteIcon />}
                          onClick={() => {
                            fetch("/delete-claim?name=" + claim.name);
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
          </>
        )}
      </div>
    </section>
  );
}

export default ClusterClaims;
