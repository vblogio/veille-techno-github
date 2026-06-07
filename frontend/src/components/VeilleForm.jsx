import React, { useState } from "react";
import { runVeille } from "../api";

const VeilleForm = ({ onVeilleComplete }) => {
    const [requetes, setRequetes] = useState([
        "(docker OR kubernetes OR k8s OR container OR containers) in:description,readme created:{date}",
        "(selfhosted OR self-hosted OR homelab OR devops OR cloud OR server) in:description,readme created:{date}",
        "(web ui OR dashboard OR frontend OR admin OR management OR orchestration) in:description,readme created:{date}"
    ].join("\n"));
    const [jours, setJours] = useState(180);
    const [maxRepos, setMaxRepos] = useState(300);
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            const result = await runVeille(
                requetes.split("\n").filter(q => q.trim()),
                jours,
                maxRepos
            );
            onVeilleComplete(result);
        } catch (error) {
            alert(`Erreur : ${error.message}`);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <h2>Lancer une nouvelle veille</h2>
            <div>
                <label htmlFor="requetes">Requêtes GitHub (une par ligne) :</label>
                <textarea
                    id="requetes"
                    value={requetes}
                    onChange={(e) => setRequetes(e.target.value)}
                    rows="5"
                    required
                />
            </div>
            <div>
                <label htmlFor="jours">Nombre de jours :</label>
                <input
                    type="number"
                    id="jours"
                    value={jours}
                    onChange={(e) => setJours(parseInt(e.target.value))}
                    min="1"
                    required
                />
            </div>
            <div>
                <label htmlFor="maxRepos">Max repos :</label>
                <input
                    type="number"
                    id="maxRepos"
                    value={maxRepos}
                    onChange={(e) => setMaxRepos(parseInt(e.target.value))}
                    min="10"
                    required
                />
            </div>
            <button type="submit" disabled={isLoading}>
                {isLoading ? "En cours..." : "Lancer la veille"}
            </button>
        </form>
    );
};

export default VeilleForm;