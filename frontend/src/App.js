import React from "react";
import ClusterPools from "./ClusterPoolsComp";
import ClusterCliams from "./ClsuerClaimsComp";
import DeleteAllClaims from "./DeleteAllClaimsComp";

function App() {
  return (
    <div className="App">
      <h1 align="center">Hive Claim System</h1>
      <ClusterPools />
      <ClusterCliams />
      <DeleteAllClaims />
    </div>
  );
}

// function App() {
//   return (
//     <div className="App">
//       <h1 align="center">Hive Claim System</h1>
//       {!Login.authenticated ? (
//         <Login />
//       ) : (
//         <>
//           <ClusterPools />
//           <ClusterCliams />
//           <DeleteAllClaims />
//         </>
//       )}
//     </div>
//   );
// }

export default App;
