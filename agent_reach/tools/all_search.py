import sys
import os
import json
import time
import socket
import concurrent.futures

# Set default socket timeout for all network requests in all threads
socket.setdefaulttimeout(3.5)

from agent_reach.tools.twitter_search import search_twitter
from agent_reach.tools.yt_search import search_youtube
from agent_reach.tools.ig_search import search_instagram
from agent_reach.tools.pin_search import search_pinterest
from agent_reach.tools.reddit_search import search_reddit
from agent_reach.tools.github_search import search_github
from agent_reach.tools.linkedin_search import search_linkedin
from agent_reach.tools.web_search import search_web

import threading

def search_all_platforms(query, per_platform=4):
    """Execute concurrent search using daemon threads with hard 3.5s cutoff."""
    tasks = [
        ("YouTube", search_youtube),
        ("GitHub", search_github),
        ("Web", search_web),
        ("Twitter", search_twitter),
        ("Reddit", search_reddit),
        ("LinkedIn", search_linkedin),
        ("Instagram", search_instagram),
        ("Pinterest", search_pinterest)
    ]
    
    all_results = []
    lock = threading.Lock()
    threads = []
    
    def worker(fn, name):
        try:
            res = fn(query, per_platform)
            if res and isinstance(res, list):
                with lock:
                    all_results.extend(res)
        except Exception:
            pass

    for name, fn in tasks:
        t = threading.Thread(target=worker, args=(fn, name), daemon=True)
        t.start()
        threads.append(t)

    # Wait at most 3.5 seconds total across all threads
    start_time = time.time()
    for t in threads:
        remaining = 3.5 - (time.time() - start_time)
        if remaining <= 0:
            break
        t.join(timeout=remaining)

    return all_results

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "3d yazıcı"
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    results = search_all_platforms(q, count)
    print(json.dumps(results, ensure_ascii=False))
