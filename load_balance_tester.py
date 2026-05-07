# load_balance_tester.py
#
# Advanced Nginx Load Balancer Verification Tool
#
# Run:
#   python load_balance_tester.py
#
# Requirements:
#   pip install requests
#
# What this tests:
#   1. Sequential round-robin balancing
#   2. Concurrent request distribution
#   3. Per-container request counts
#   4. Response timing
#   5. Failure detection
#   6. Sticky connection behavior
#   7. Stress testing
#   8. Live monitoring mode
#
# Assumes:
#   GET /whoami returns:
#   {"container": "fastapi_app1"}

import requests
import threading
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter

URL = "http://localhost:8000/whoami"

# ============================================
# CORE REQUEST FUNCTION
# ============================================

def make_request(session=None):
    start = time.time()

    try:
        if session:
            r = session.get(URL, timeout=5)
        else:
            r = requests.get(URL, timeout=5)

        elapsed = round((time.time() - start) * 1000, 2)

        if r.status_code != 200:
            return {
                "success": False,
                "status": r.status_code,
                "time": elapsed,
                "container": None
            }

        data = r.json()

        return {
            "success": True,
            "status": 200,
            "time": elapsed,
            "container": data.get("container", "unknown")
        }

    except Exception as e:
        elapsed = round((time.time() - start) * 1000, 2)

        return {
            "success": False,
            "status": "ERROR",
            "time": elapsed,
            "container": None,
            "error": str(e)
        }


# ============================================
# SEQUENTIAL ROUND ROBIN TEST
# ============================================

def sequential_test(count=12):
    print("\n" + "=" * 60)
    print("SEQUENTIAL ROUND-ROBIN TEST")
    print("=" * 60)

    results = []

    for i in range(count):
        result = make_request()
        results.append(result)

        print(
            f"[{i+1:02}] "
            f"Container: {result['container']} | "
            f"Status: {result['status']} | "
            f"Time: {result['time']}ms"
        )

    containers = [r["container"] for r in results if r["container"]]
    counts = Counter(containers)

    print("\nDistribution:")
    for k, v in counts.items():
        print(f"  {k}: {v}")

    return results


# ============================================
# CONCURRENT LOAD TEST
# ============================================

def concurrent_test(total_requests=100, workers=20):
    print("\n" + "=" * 60)
    print("CONCURRENT LOAD TEST")
    print("=" * 60)

    results = []

    start_total = time.time()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(make_request)
            for _ in range(total_requests)
        ]

        completed = 0

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

            completed += 1

            print(
                f"\rCompleted: {completed}/{total_requests}",
                end=""
            )

    total_time = round(time.time() - start_total, 2)

    print("\n")

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    containers = [r["container"] for r in successful]
    counts = Counter(containers)

    response_times = [r["time"] for r in successful]

    print(f"Total Requests: {total_requests}")
    print(f"Successful:     {len(successful)}")
    print(f"Failed:         {len(failed)}")
    print(f"Total Time:     {total_time}s")

    print("\nContainer Distribution:")
    for k, v in counts.items():
        percentage = round((v / len(successful)) * 100, 2)
        print(f"  {k}: {v} requests ({percentage}%)")

    if response_times:
        print("\nResponse Times:")
        print(f"  Min:     {min(response_times)}ms")
        print(f"  Max:     {max(response_times)}ms")
        print(f"  Avg:     {round(statistics.mean(response_times), 2)}ms")
        print(f"  Median:  {round(statistics.median(response_times), 2)}ms")

    if failed:
        print("\nErrors:")
        for r in failed[:5]:
            print(r.get("error"))

    return results


# ============================================
# KEEP-ALIVE / SESSION TEST
# ============================================

def session_stickiness_test(count=10):
    print("\n" + "=" * 60)
    print("SESSION / KEEP-ALIVE TEST")
    print("=" * 60)

    session = requests.Session()

    containers = []

    for i in range(count):
        result = make_request(session=session)

        containers.append(result["container"])

        print(
            f"[{i+1:02}] "
            f"{result['container']} "
            f"({result['time']}ms)"
        )

    unique = set(containers)

    print("\nUnique Containers Hit:", len(unique))
    print(unique)

    if len(unique) == 1:
        print("\nNOTE:")
        print("Connection reuse detected.")
        print("Nginx may keep sending requests over same TCP connection.")

    return containers


# ============================================
# LIVE MONITOR MODE
# ============================================

def live_monitor(interval=1):
    print("\n" + "=" * 60)
    print("LIVE MONITOR")
    print("=" * 60)

    print("Press CTRL+C to stop.\n")

    try:
        while True:
            result = make_request()

            print(
                f"{time.strftime('%H:%M:%S')} | "
                f"{result['container']} | "
                f"{result['time']}ms"
            )

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nStopped.")


# ============================================
# STRESS TEST
# ============================================

def stress_test(rounds=5, requests_per_round=200):
    print("\n" + "=" * 60)
    print("STRESS TEST")
    print("=" * 60)

    for i in range(rounds):
        print(f"\nROUND {i+1}/{rounds}")

        concurrent_test(
            total_requests=requests_per_round,
            workers=50
        )

        time.sleep(1)


# ============================================
# MENU
# ============================================

def menu():
    while True:
        print("\n" + "=" * 60)
        print("NGINX LOAD BALANCER TESTER")
        print("=" * 60)

        print("1. Sequential Round-Robin Test")
        print("2. Concurrent Load Test")
        print("3. Session Stickiness Test")
        print("4. Live Monitor")
        print("5. Stress Test")
        print("6. Exit")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            sequential_test()

        elif choice == "2":
            concurrent_test()

        elif choice == "3":
            session_stickiness_test()

        elif choice == "4":
            live_monitor()

        elif choice == "5":
            stress_test()

        elif choice == "6":
            break

        else:
            print("Invalid option.")


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    menu()