import sys
import os
import json
import time
import concurrent.futures

from agent_reach.tools.twitter_search import search_twitter
from agent_reach.tools.yt_search import search_youtube
from agent_reach.tools.ig_search import search_instagram
from agent_reach.tools.pin_search import search_pinterest
from agent_reach.tools.reddit_search import search_reddit
from agent_reach.tools.github_search import search_github
from agent_reach.tools.linkedin_search import search_linkedin
from agent_reach.tools.web_search import search_web

def search_all_platforms(query, per_platform=10):
    """Execute high-speed concurrent search across all 8 active social & web channels."""
    tasks = [
        ("Twitter", search_twitter),
        ("YouTube", search_youtube),
        ("Instagram", search_instagram),
        ("Pinterest", search_pinterest),
        ("Reddit", search_reddit),
        ("GitHub", search_github),
        ("LinkedIn", search_linkedin),
        ("Web", search_web)
    ]
    
    all_results = []
    
    def run_one(name_fn):
        name, fn = name_fn
        try:
            return fn(query, per_platform)
        except Exception:
            return []

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        results = executor.map(run_one, tasks)
        for res_list in results:
            if res_list:
                all_results.extend(res_list)

    return all_results

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "3d yazıcı"
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    results = search_all_platforms(q, count)
    print(json.dumps(results, ensure_ascii=False))
