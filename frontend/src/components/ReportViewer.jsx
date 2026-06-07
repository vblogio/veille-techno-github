import React from "react";

const ReportViewer = ({ htmlContent }) => {
    return (
        <div>
            <h2>Rapport de veille</h2>
            <div dangerouslySetInnerHTML={{ __html: htmlContent }} />
        </div>
    );
};

export default ReportViewer;