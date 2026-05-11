import json
from main import run_learning_loop

def run_benchmark():
    # 1. Clear the memory block for a fresh, unbiased system run
    with open("src/memory.json", "w") as f:
        f.write("[]")
    with open("src/audit_log.json", "w") as f:
        f.write("")
        
    # 2. Define a suite of constraints-based tasks
    tasks = [
        {
            "id": "Task 1 (String Reversal)",
            "prompt": "Write a Python function to reverse a string. CRITICAL CONSTRAINT: You must NOT use string slicing like [::-1] or the built-in reversed() function. Use a loop."
        },
        {
            "id": "Task 2 (Palindrome)",
            "prompt": "Write a Python function to check if a string is a palindrome. CRITICAL CONSTRAINT: You must NOT use string slicing [::-1] or reversed()."
        },
        {
            "id": "Task 3 (Anagram Check)",
            "prompt": "Write a Python function to check if two strings are anagrams. CRITICAL CONSTRAINT: You must NOT use sorted(), sort(), or Counter from collections."
        }
    ]

    print("==================================================")
    print("STARTING COLLECTIVE-SYSTEM EVALUATION BENCHMARK")
    print("==================================================\n")
    
    results = []
    
    # 3. Execute the Learning Loop for each task
    for t in tasks:
        metrics = run_learning_loop(t["id"], t["prompt"], max_iterations=5)
        results.append({
            "Task": t["id"],
            "Metrics": metrics
        })
        
    # 4. Generate the final empirical report
    print("\n" + "="*50)
    print("BENCHMARK REPORT (Agentic Services Computing)")
    print("="*50)
    
    total_ct = 0
    total_cd = 0
    total_gar = 0
    total_sd = 0
    total_bv = 0
    recoveries = 0
    passes = 0
    failures_tolerated = 0
    
    for r in results:
        m = r["Metrics"]
        total_ct += m["CT"]
        total_cd += m["CD"]
        total_gar += m["GAR"]
        total_sd += m["SD"]
        total_bv += m["BV"]
        failures_tolerated += m["FT"]
        if m["RR"]: recoveries += 1
        if m["Task_Passed"]: passes += 1
        
        print(f"\n- {r['Task']}")
        print(f"  Passed: {m['Task_Passed']}")
        print(f"  Iterations (CT): {m['CT']}")
        print(f"  Coordination Density (CD): {m['CD']}")
        print(f"  Goal Agreement Rate (GAR): {m['GAR']:.2f}")
        print(f"  Strategy Diversity (SD): {m['SD']}")
        print(f"  Recovery Rate (RR): {m['RR']}")
        
    print("\n" + "-" * 50)
    print("SYSTEM AVERAGES (TABLE IV METRICS):")
    print("-" * 50)
    print(f"Total Tasks Passed: {passes}/{len(tasks)}")
    print(f"Avg Collective Throughput (CT): {total_ct / max(1, len(tasks)):.2f} iterations")
    print(f"Avg Coordination Density (CD): {total_cd / max(1, len(tasks)):.2f} interactions")
    print(f"Avg Goal Agreement Rate (GAR): {total_gar / max(1, len(tasks)):.2f}")
    print(f"Avg Strategy Diversity (SD): {total_sd / max(1, len(tasks)):.2f}")
    
    # Calculate global RSpI from the last task run since it aggregates audit log
    avg_rspi = sum(r["Metrics"]["RSpI"] for r in results) / max(1, len(tasks))
    print(f"Role Specialization Index (RSpI): {avg_rspi:.2f} (Action Entropy)")
    
    print(f"Avg Behavioral Variance (BV): {total_bv / max(1, len(tasks)):.2f}")

    print(f"Total Recovered Failures (RR): {recoveries}")
    print(f"Total Critic Failures Tolerated (FT): {failures_tolerated}")
    print("==================================================\n")

if __name__ == '__main__':
    run_benchmark()