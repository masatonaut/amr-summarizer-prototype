// frontend/src/App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import InputForm from "./InputForm";
import ResultsDisplay from "./ResultsDisplay";
import "./App.css";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<InputForm />} />
        <Route path="/results" element={<ResultsDisplay />} />
      </Routes>
    </Router>
  );
}

export default App;
