import React, { useEffect, useState } from "react";
import { getHistory } from "../api";

const HistoryList = ({ onSelectReport }) => {
    const [rapports, setRapports] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const data = await getHistory();
                setRapports(data);
            } catch (error) {
                alert(`Erreur : ${error.message}`);
            } finally {
                setIsLoading(false);
            }
        };
        fetchHistory();
    }, []);

    return (
        <div>
            <h2>Historique des rapports</h2>
            {isLoading ? (
                <p>Chargement...</p>
            ) : rapports.length === 0 ? (
                <p>Aucun rapport disponible.</p>
            ) : (
                <ul>
                    {rapports.map((rapport) => (
                        <li key={rapport.file}>
                            <a
                                href={`/output/${rapport.file}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                onClick={(e) => {
                                    e.preventDefault();
                                    onSelectReport(rapport.file);
                                }}
                            >
                                {rapport.date} - {rapport.count} outils
                            </a>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default HistoryList;