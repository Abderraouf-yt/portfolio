import os
import re
import urllib.request
import json
from datetime import datetime

# Configuration
GITHUB_USERNAME = "Abderraouf-yt"
API_URL = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100&sort=updated"
INDEX_FILE = "index.html"
FEATURED_TOPIC = "portfolio-featured"

MARKER_START = "<!-- START_GITHUB_SYNC -->"
MARKER_END = "<!-- END_GITHUB_SYNC -->"

def fetch_repos():
    headers = {
        "User-Agent": "Portfolio-Sync-Script",
        "Accept": "application/vnd.github.v3+json"
    }
    
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
        
    req = urllib.request.Request(API_URL, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data
    except Exception as e:
        print(f"Error fetching repositories: {e}")
        return []

def filter_and_sort_repos(repos):
    featured = []
    for repo in repos:
        topics = repo.get("topics", [])
        if FEATURED_TOPIC in topics:
            featured.append(repo)
            
    # GitHub API usually sorts by updated_at, but we sort again to be sure
    featured.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return featured

def generate_html(repos):
    if not repos:
        return "                <!-- No featured repositories found. -->\n"
        
    html_out = ""
    for idx, repo in enumerate(repos):
        name = repo.get("name", "Unknown Repository").replace("-", " ").title()
        description = repo.get("description") or "No description provided."
        url = repo.get("html_url", "#")
        language = repo.get("language")
        topics = [t for t in repo.get("topics", []) if t != FEATURED_TOPIC]
        
        # Determine status badge color based on index or just use a default
        colors = ["blue", "purple", "green", "orange", "red"]
        color = colors[idx % len(colors)]
        
        # Build tech tags
        tech_tags_html = ""
        if language:
            tech_tags_html += f'                        <span class="tech-tag">{language}</span>\n'
        for topic in topics[:4]: # Limit to 4 additional topics
            tech_tags_html += f'                        <span class="tech-tag">{topic}</span>\n'
            
        repo_html = f"""
                <!-- Project: {name} -->
                <div class="project-card">
                    <div class="project-header">
                        <span class="status-badge status-{color}">GitHub Repo</span>
                        <h3 class="project-title">{name}</h3>
                    </div>
                    
                    <div class="project-problem">
                        <strong>Description:</strong> {description}
                    </div>
                    
                    <div class="project-impact">
                        <h4>Details:</h4>
                        <ul>
                            <li>⭐ {repo.get("stargazers_count", 0)} Stars</li>
                            <li>🔄 Updated: {datetime.strptime(repo.get("updated_at", "2000-01-01T00:00:00Z").split("T")[0], "%Y-%m-%d").strftime("%B %d, %Y")}</li>
                        </ul>
                    </div>
                    
                    <div class="tech-stack">
{tech_tags_html}                    </div>
                    
                    <a href="{url}" target="_blank" rel="noopener noreferrer" class="project-cta" style="text-decoration: none;">
                        View Repository
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                    </a>
                </div>
"""
        html_out += repo_html
        
    return html_out

def update_index_html(html_content):
    if not os.path.exists(INDEX_FILE):
        print(f"Error: {INDEX_FILE} not found in current directory: {os.getcwd()}")
        return False
        
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        
    pattern = re.compile(f"({MARKER_START}).*?({MARKER_END})", re.DOTALL)
    
    if not pattern.search(content):
        print("Error: Could not find START and END markers in index.html")
        return False
        
    new_content = pattern.sub(f"\\1\n{html_content}                \\2", content)
    
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    print("Successfully updated index.html with latest GitHub repositories.")
    return True

if __name__ == "__main__":
    print("Fetching repositories...")
    repos = fetch_repos()
    print(f"Found {len(repos)} total repositories.")
    
    featured_repos = filter_and_sort_repos(repos)
    print(f"Found {len(featured_repos)} repositories tagged with '{FEATURED_TOPIC}'.")
    
    html_content = generate_html(featured_repos)
    update_index_html(html_content)
