import axios from "axios";

const API_BASE_URL =   "/api";

export const runVeille = async (requetes, jours, maxRepos) => {
    const response = await axios.post(`${API_BASE_URL}/run-veille`, {
        requetes,
        jours,
        max_repos: maxRepos,
    });
    return response.data;
};

export const getHistory = async () => {
    const response = await axios.get(`${API_BASE_URL}/history`);
    return response.data.rapports;
};

export const updateQueries = async (requetes) => {
    const response = await axios.put(`${API_BASE_URL}/queries`, { requetes });
    return response.data;
};