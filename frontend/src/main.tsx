import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "./App";
import UploadPage from "./pages/UploadPage";
import ScorecardPage from "./pages/ScorecardPage";
import SharePage from "./pages/SharePage";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />}>
          <Route index element={<UploadPage />} />
          <Route path="results/:sessionId" element={<ScorecardPage />} />
          <Route path="share/:sessionId" element={<SharePage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
