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
import PropTypes from "prop-types";
import Box from "@mui/material/Box";
import DownloadIcon from "@mui/icons-material/Download";
import Collapse from "@mui/material/Collapse";
import IconButton from "@mui/material/IconButton";
import Typography from "@mui/material/Typography";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";

function Row(props) {
  const { row: claim } = props;
  const [open, setOpen] = React.useState(false);

  return (
    <React.Fragment>
      <TableRow
        key={claim.name}
        sx={{
          "&:last-child td, &:last-child th": { border: 0 },
        }}
      >
        <TableCell>
          <IconButton
            aria-label="expand row"
            size="small"
            onClick={() => setOpen(!open)}
          >
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell component="th" scope="row">
          {claim.name}
        </TableCell>
        <TableCell align="center">{claim.pool}</TableCell>
        <TableCell align="center">{claim.namespace}</TableCell>

        <TableCell align="center">
          <Button
            color="error"
            startIcon={<DeleteIcon />}
            onClick={() => {
              fetch("http://localhost:5000/delete-claim?name=" + claim.name);
            }}
          >
            {" "}
            Delete{" "}
          </Button>
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 1 }}>
              <Typography
                variant="h6"
                gutterBottom
                component="div"
              ></Typography>
              <Table size="small" aria-label="purchases">
                <TableHead>
                  <TableRow>
                    <TableCell align="center"></TableCell>
                    <TableCell align="center"></TableCell>
                    <TableCell align="center"></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {claim.info.map((info) => (
                    <TableRow key={info.name}>
                      <TableCell>
                        <a
                          href={info.console}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          Console
                        </a>
                      </TableCell>
                      <TableCell align="center">
                        <p>
                          {info.creds.split(":")[0]} <br />
                          {info.creds.split(":")[1]}
                        </p>
                      </TableCell>
                      <TableCell align="center">
                        <Button
                          endIcon={<DownloadIcon />}
                          href={"http://localhost:5000/" + info.kubeconfig}
                        >
                          Kubeconfig
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </React.Fragment>
  );
}

Row.propTypes = {
  row: PropTypes.shape({
    name: PropTypes.string.isRequired,
    pool: PropTypes.string.isRequired,
    namespace: PropTypes.string.isRequired,
    info: PropTypes.arrayOf(
      PropTypes.shape({
        console: PropTypes.string.isRequired,
        creds: PropTypes.string.isRequired,
        kubeconfig: PropTypes.string.isRequired,
      }),
    ).isRequired,
  }).isRequired,
};

function ClusterClaims() {
  const [clusterClaims, setClusterClaims] = useState([]);

  const getClusterClaims = async () => {
    const res = await fetch("http://localhost:5000/cluster-claims");
    const data = await res.json();
    setClusterClaims(data);
  };

  useEffect(() => {
    getClusterClaims();
  }, []);

  return (
    <>
      <h3>Active Claims</h3>
      <TableContainer component={Paper}>
        <Table aria-label="collapsible table">
          <TableHead>
            <TableRow>
              <TableCell></TableCell>
              <TableCell>Name</TableCell>
              <TableCell align="center">Poll</TableCell>
              <TableCell align="center">Namespace</TableCell>
            </TableRow>
          </TableHead>

          <TableBody>
            {clusterClaims.map((claim) => (
              <Row key={claim.name} row={claim} />
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </>
  );
}

export default ClusterClaims;
