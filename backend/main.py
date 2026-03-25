import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from datetime import datetime, timedelta
from database import SessionLocal, ProfileCache, init_db

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables when the server starts
init_db()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def get_user_repos(username: str):
    url = f"https://api.github.com/users/{username}/repos?sort=pushed&per_page=30"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 404:
        raise HTTPException(status_code=404, detail="GitHub user not found")
    return res.json()

def get_language_stats(repos: list):
    languages = {}
    for repo in repos:
        lang = repo.get("language")
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
    return languages

def get_commit_stats(username: str, repos: list):
    total_commits = 0
    repo_count = 0
    for repo in repos[:5]:
        repo_name = repo["name"]
        url = f"https://api.github.com/repos/{username}/{repo_name}/commits?per_page=10&author={username}"
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            total_commits += len(res.json())
            repo_count += 1
    avg_commits = total_commits / repo_count if repo_count > 0 else 0
    return {
        "total_commits_sampled": total_commits,
        "avg_commits_per_repo": round(avg_commits, 1)
    }

@app.get("/analyze/{username}")
def analyze(username: str):
    db = SessionLocal()

    try:
        # Check if we have a fresh cached result (less than 24 hours old)
        cached = db.query(ProfileCache).filter(
            ProfileCache.username == username
        ).first()

        if cached:
            age = datetime.utcnow() - cached.cached_at
            if age < timedelta(hours=24):
                print(f"Cache hit for {username}")  # you'll see this in terminal
                return cached.data  # return saved result, no GitHub API call!

        # No cache or cache is old — fetch fresh data
        print(f"Cache miss for {username}, fetching from GitHub...")
        repos = get_user_repos(username)
        language_stats = get_language_stats(repos)
        commit_stats = get_commit_stats(username, repos)

        result = {
            "username": username,
            "stats": {
                "public_repos": len(repos),
                "total_stars": sum(r["stargazers_count"] for r in repos),
                "total_forks": sum(r["forks_count"] for r in repos),
                "repos_with_descriptions": sum(1 for r in repos if r.get("description")),
                "languages": language_stats,
                "commit_stats": commit_stats
            }
        }

        # Save to database — upsert (update if exists, insert if not)
        if cached:
            cached.data = result
            cached.cached_at = datetime.utcnow()
        else:
            db.add(ProfileCache(username=username, data=result))

        db.commit()
        return result

    finally:
        db.close()  # always close the DB session