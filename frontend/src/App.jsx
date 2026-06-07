import React, { useState } from "react";
import VeilleForm from "./components/VeilleForm";
import HistoryList from "./components/HistoryList";
import ReportViewer from "./components/ReportViewer";
import "./App.css";

const App = () => {
    const [currentReport, setCurrentReport] = useState(null);
    const [rapportHtml, setRapportHtml] = useState("");

    const handleVeilleComplete = (result) => {
        setRapportHtml(result.rapport_html);
        setCurrentReport(result.file);
    };

    const handleSelectReport = async (filename) => {
        try {
            const response = await fetch(`/output/${filename}`);
            const html = await response.text();
            setRapportHtml(html);
            setCurrentReport(filename);
        } catch (error) {
            alert(`Erreur : ${error.message}`);
        }
    };

    return (
        <div className="container">
            <h1>Veille Outils Open Source</h1>
            <VeilleForm onVeilleComplete={handleVeilleComplete} />
            <hr />
            <HistoryList onSelectReport={handleSelectReport} />
            {currentReport && (
                <>
                    <hr />
                    <ReportViewer htmlContent={rapportHtml} />
                </>
            )}
        </div>
    );
};

export default App;