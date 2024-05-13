import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "./App";
import Login from "./Login";
import NotFound from "./NotFound";

const Router = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" exact element={<App />} />
        <Route path="/login" exact element={<Login />} />
        <Route element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
};

export default Router;
