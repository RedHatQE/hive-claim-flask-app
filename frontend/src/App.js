import React from "react";
import ClusterPools from "./ClusterPoolsComp";
import ClusterCliams from "./ClsuerClaimsComp";
import DeleteAllClaims from "./DeleteAllClaimsComp";

function App() {
  return (
    <div className="App">
      <h3>Hive Claim System</h3>
      <ClusterPools />
      <ClusterCliams />
      <DeleteAllClaims />
    </div>
  );
}

export default App;
