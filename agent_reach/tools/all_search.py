import sys
import os
import json
import time
import socket
import concurrent.futures

# Set default socket timeout for all network requests in all threads
socket.setdefaulttimeout(5.0)

from agent_reach.tools.twitter_search import search_twitter
from agent_reach.tools.yt_search import search_youtube
from agent_reach.tools.ig_search import search_instagram
from agent_reach.tools.pin_search import search_pinterest
from agent_reach.tools.reddit_search import search_reddit
from agent_reach.tools.github_search import search_github
from agent_reach.tools.linkedin_search import search_linkedin
from agent_reach.tools.web_search import search_web

def search_all_platforms(query, per_platform=5):
    """Execute high-speed concurrent search across all 8 active social & web channels with strict 6s cutoff."""
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
    
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=8)
    try:
        future_to_name = {
            executor.submit(fn, query, per_platform): name 
            for name, fn in tasks
        }
        
        done, not_done = concurrent.futures.wait(
            future_to_name.keys(), 
            timeout=6.0, 
            return_when=concurrent.futures.ALL_COMPLETED
        )
        
        for future in done:
            try:
                res = future.result()
                if res and isinstance(res, list):
                    all_results.extend(res)
            except Exception:
                pass
    finally:
        # Do not wait for hanging threads on shutdown
        try:
            executor.shutdown(wait=False, cancel_futures=True)
        except Exception:
            executor.shutdown(wait=False)

    return all_results

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "3d yazıcı"
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    results = search_all_platforms(q, count)
    print(json.dumps(results, ensure_ascii=False))
