import os
import requests
from datetime import datetime, timedelta
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .utils import charger_cache, sauvegarder_cache, est_cache_valide
from typing import List

class VeilleService:
    def __init__(self, github_token: str, mistral_api_key: str):
        self.github_token = github_token
        self.mistral_api_key = mistral_api_key
        self.llm = ChatMistralAI(
            model="mistral-medium",
            temperature=0.7,
            api_key=mistral_api_key
        )
        self.cache = charger_cache()

    def a_docker_compose(self, repo_full_name: str) -> bool:
        cache_key = f"docker_compose:{repo_full_name}"
        if cache_key in self.cache and est_cache_valide(self.cache[cache_key]):
            return self.cache[cache_key]["result"]

        url = f"https://api.github.com/repos/{repo_full_name}/contents/docker-compose.yml"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        try:
            response = requests.get(url, headers=headers, timeout=5)
            result = response.status_code == 200
        except Exception:
            result = False

        self.cache[cache_key] = {
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        sauvegarder_cache(self.cache)
        return result

    def rechercher_repos_github(self, liste_requetes: list, jours: int = 180, max_repos: int = 300) -> list:
        date_cutoff = (datetime.now() - timedelta(days=jours)).strftime("%Y-%m-%d")
        repos = []

        for query in liste_requetes:
            query = query.replace("{date}", date_cutoff)
            cache_key = f"search:{query}"
            if cache_key in self.cache and est_cache_valide(self.cache[cache_key]):
                repos.extend(self.cache[cache_key]["result"])
                continue

            url_base = f"https://api.github.com/search/repositories?q={query}&sort=created&order=desc&per_page=100"
            page = 1
            repos_query = []

            while len(repos_query) < max_repos:
                url = f"{url_base}&page={page}"
                headers = {"Authorization": f"token {self.github_token}"}
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    if not data.get("items"):
                        break
                    repos_query.extend([
                        {
                            "nom": repo["name"],
                            "lien": repo["html_url"],
                            "description": repo["description"] or "Aucune description",
                            "date": repo["created_at"],
                            "stars": repo["stargazers_count"],
                            "langage": repo["language"]
                        } for repo in data["items"]
                    ])
                    page += 1
                except Exception:
                    break

            self.cache[cache_key] = {
                "result": repos_query,
                "timestamp": datetime.now().isoformat()
            }
            sauvegarder_cache(self.cache)
            repos.extend(repos_query)
            if len(repos) >= max_repos:
                break

        return repos[:max_repos]

    def filtrer_repos(self, repos: list) -> list:
        repos_filtres = []
        for repo in repos:
            repo_full_name = repo["lien"].split("https://github.com/")[1]
            if self.a_docker_compose(repo_full_name):
                repos_filtres.append(repo)
        return repos_filtres

    def generer_top_5(self, repos: list) -> str:
        repos_trie = sorted(repos, key=lambda x: x["stars"], reverse=True)[:5]
        prompt = ChatPromptTemplate.from_template(
            """Tu es un rédacteur technique spécialisé en DevOps.
            À partir de la liste des 5 outils ci-dessous, rédige une section "Top 5 outils" pour un rapport de veille.
            Pour chaque outil, écris UN PARAGRAPHE avec :
            - Nom et lien (format HTML : <a href="URL">Nom</a>)
            - Description courte
            - Pourquoi c'est intéressant
            - Nombre d'étoiles (⭐ X) et langage principal
            Outils à analyser :
            {outils}
            Format de sortie : HTML valide (SEULEMENT la section Top 5).
            """
        )
        chain = prompt | self.llm | StrOutputParser()
        outils_str = "\n".join(
            f"- {repo['nom']} ({repo['lien']}) : {repo['description']} (⭐ {repo['stars']}, {repo['langage'] or 'N/A'})"
            for repo in repos_trie
        )
        return chain.invoke({"outils": outils_str})

    def generer_rapport_html(self, repos: list) -> str:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        top_5_html = self.generer_top_5(repos)
        tableau_html = """
        <table>
            <thead>
                <tr>
                    <th>Nom</th>
                    <th>Lien</th>
                    <th>Description</th>
                    <th>Date</th>
                    <th>⭐ Étoiles</th>
                    <th>Langage</th>
                </tr>
            </thead>
            <tbody>
        """
        for repo in repos:
            tableau_html += f"""
                <tr>
                    <td><a href="{repo['lien']}">{repo['nom']}</a></td>
                    <td><a href="{repo['lien']}" target="_blank">Lien</a></td>
                    <td>{repo['description'] or 'Aucune description'}</td>
                    <td>{repo['date'][:10]}</td>
                    <td><span class="stars">⭐ {repo['stars']}</span></td>
                    <td>{repo['langage'] or 'N/A'}</td>
                </tr>
            """
        tableau_html += "</tbody></table>"

        html = f"""
        <!DOCTYPE html>
        <html lang="fr" data-theme="auto">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Veille Outils Open Source - {date[:10]}</title>
            <link rel="stylesheet" href="https://unpkg.com/@picocss/pico@latest/css/pico.min.css">
            <style>
                :root {{
                    --primary: #0066cc;
                    --stars-color: #ff9900;
                }}
                .stars {{ color: var(--stars-color); font-weight: bold; }}
                table {{ width: 100%; margin: 1rem 0; }}
                th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: var(--primary-light); }}
            </style>
        </head>
        <body>
            <main class="container">
                <h1>Veille Outils Open Source</h1>
                <p>Généré le {date}</p>
                <section>
                    <h2>Top 5 outils</h2>
                    {top_5_html}
                </section>
                <section>
                    <h2>Tableau récapitulatif</h2>
                    {tableau_html}
                </section>
            </main>
        </body>
        </html>
        """
        return html

    def run_veille(self, requetes: list, jours: int = 180, max_repos: int = 300) -> dict:
        repos = self.rechercher_repos_github(requetes, jours, max_repos)
        repos_filtres = self.filtrer_repos(repos)
        rapport_html = self.generer_rapport_html(repos_filtres) if repos_filtres else "<p>Aucun outil trouvé.</p>"
        return {
            "status": "success",
            "count": len(repos_filtres),
            "rapport_html": rapport_html,
            "timestamp": datetime.now().isoformat()
        }
