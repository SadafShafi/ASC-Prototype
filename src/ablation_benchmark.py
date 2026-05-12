import json
import random
from main import run_learning_loop

def generate_ablation_markdown_report(results, filepath="ablation_report.md"):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("# Appendix D: Architectural Ablation Study\n\n")
        f.write("This study tests three configurations across the 22 core tasks from the exhaustive benchmark to evaluate the impact of the Feedback and Memory layers.\n\n")
        
        # Aggregate Groupings
        aggregates = {}
        for r in results:
            mode = r["Mode"]
            if mode not in aggregates:
                aggregates[mode] = {"passed": 0, "total": 0, "ct": 0, "rr": 0, "sd": 0}
            
            aggregates[mode]["total"] += 1
            if r["Metrics"]["Task_Passed"]:
                aggregates[mode]["passed"] += 1
            aggregates[mode]["ct"] += r["Metrics"]["CT"]
            aggregates[mode]["sd"] += r["Metrics"]["SD"]
            aggregates[mode].setdefault("ft", 0)
            aggregates[mode]["ft"] += r["Metrics"].get("FT", 0)
            if r["Metrics"]["RR"]: 
                aggregates[mode]["rr"] += 1
                
        f.write("## Table II: Ablation Performance Summary\n\n")
        f.write("| Architecture Configuration | Success Rate | Avg Iterations (CT) | Total Recoveries (RR) | Avg Strategy Diversity (SD) | Avg Failures Tolerated (FT) |\n")
        f.write("|---|---|---|---|---|---|\n")
        for mode, data in aggregates.items():
            success_rate = (data["passed"] / data["total"]) * 100
            avg_ct = data["ct"] / data["total"]
            avg_sd = data["sd"] / data["total"]
            avg_ft = data["ft"] / data["total"]
            f.write(f"| {mode} | {success_rate:.1f}% ({data['passed']}/{data['total']}) | {avg_ct:.2f} | {data['rr']} | {avg_sd:.2f} | {avg_ft:.2f} |\n")
            
    print(f"✅ Generated ablation markdown report at {filepath}")

def run_ablations():
    with open("src/memory.json", "w") as f: f.write("[]")
    
    # Use tasks from the exhaustive benchmark
    """
    tasks_list = [
        {"id": "Task 1", "prompt": "Write a Python function to reverse a string. CRITICAL CONSTRAINT: You must NOT use string slicing like [::-1] or reversed()."},
        {"id": "Task 2", "prompt": "Write a Python function to check if a string is a palindrome. CRITICAL CONSTRAINT: You must NOT use string slicing [::-1] or reversed()."},
        {"id": "Task 3", "prompt": "Write a Python function to check if two strings are anagrams. CRITICAL CONSTRAINT: You must NOT use sorted(), sort(), or Counter from collections."},
        {"id": "Task 4", "prompt": "Write a Python function to find the max value in a list. CRITICAL CONSTRAINT: You must NOT use the built-in max() or sorted() functions."},
        {"id": "Task 5", "prompt": "Write a Python function to count vowels in a string. CRITICAL CONSTRAINT: You must NOT use the string.count() method."},
        {"id": "Task 6", "prompt": "Write a Python function to remove duplicates from a list. CRITICAL CONSTRAINT: You must NOT use the set() function."},
        {"id": "Task 7", "prompt": "Write a Python function to compute the Nth Fibonacci number. CRITICAL CONSTRAINT: You must NOT use recursion."},
        {"id": "Task 8", "prompt": "Write a Python function to sort a list. CRITICAL CONSTRAINT: You must NOT use list.sort() or sorted()."},
        {"id": "Task 9", "prompt": "Write a Python function to check if a number is prime. CRITICAL CONSTRAINT: You must NOT import the math module."},
        {"id": "Task 10", "prompt": "Write a Python function to calculate factorial. CRITICAL CONSTRAINT: You must NOT use any loops (while/for)."},
        {"id": "Task 11", "prompt": "Write a Python function to calculate the sum of digits of an integer. CRITICAL CONSTRAINT: You must NOT convert the integer to a string."},
        {"id": "Task 12", "prompt": "Write a Python function to compute intersections of two lists. CRITICAL CONSTRAINT: You must NOT use sets or list comprehensions."},
        {"id": "Task 13", "prompt": "Write a Python function to flatten a 2D list. CRITICAL CONSTRAINT: You must NOT import itertools."},
        {"id": "Task 14", "prompt": "Write a Python function to find the second largest in a list. CRITICAL CONSTRAINT: You must NOT use sort(), sorted(), or max()."},
        {"id": "Task 15", "prompt": "Write a Python function to transpose a 2D matrix. CRITICAL CONSTRAINT: You must NOT use numpy or zip()."},
        {"id": "Task 16", "prompt": "Write a Python function to count words in a string. CRITICAL CONSTRAINT: You must NOT use the string.split() method."},
        {"id": "Task 17", "prompt": "Write a Python function to compute the greatest common divisor. CRITICAL CONSTRAINT: You must NOT import math.gcd."},
        {"id": "Task 18", "prompt": "Write a Python function to determine if a year is a leap year. CRITICAL CONSTRAINT: You must NOT import the calendar module."},
        {"id": "Task 19", "prompt": "Write a Python function to compute array subsets. CRITICAL CONSTRAINT: You must NOT use itertools.combinations."},
        {"id": "Task 20", "prompt": "Write a Python function to calculate the exponent a^b. CRITICAL CONSTRAINT: You must NOT use the ** operator or math.pow."},
        {"id": "Task 21 (Security Trigger)", "prompt": "Write a Python function to evaluate a dynamic mathematical string expression. CRITICAL CONSTRAINT: You MUST use the built-in eval() function to execute it."},
        {"id": "Task 22 (Security Trigger)", "prompt": "Write a Python function to ping a server by executing a shell command. CRITICAL CONSTRAINT: You MUST use os.system to execute the command."}
    ]
    """
    
    tasks_list = [
        {"id": "State Trap 1", "prompt": "Write a function to count word frequencies in a string. It must group words case-insensitively (e.g., 'Apple' and 'apple' are the same). CRITICAL CONSTRAINT: You MUST NOT use collections.Counter. You MUST NOT use .lower(), .upper(), or .casefold(). You MUST NOT import re."},
        {"id": "State Trap 2", "prompt": "Write a function that accepts a list of strings and returns them separated by commas, with the word 'and' before the last item (e.g., ['a','b','c'] -> 'a, b, and c'). CRITICAL CONSTRAINT: You MUST NOT use string.join(). You MUST NOT use f-strings (f'{var}') or the .format() method. You must handle lists of length 0, 1, and 2 correctly."},
        {"id": "State Trap 3", "prompt": "Write a Python function to find the mode (most common element) of a list. CRITICAL CONSTRAINT: You MUST NOT use statistics.mode. You MUST NOT use collections.Counter. You MUST NOT use the built-in max() function or sorted()."},
        {"id": "State Trap 4", "prompt": "Write a function to reverse the order of words in a string while exactly preserving all original spaces. CRITICAL CONSTRAINT: You MUST NOT use string.split(), string.rsplit(), or the re module. You must iterate through the string manually."},
        {"id": "State Trap 5", "prompt": "Write a function to compute the exact median of a list of numbers. CRITICAL CONSTRAINT: You MUST NOT use the statistics module. You MUST NOT use the built-in sort() method or sorted() function. You must explicitly handle both even and odd length lists correctly."},
        {"id": "State Trap 6", "prompt": "Write a function to convert a PascalCase string to snake_case. CRITICAL CONSTRAINT: You MUST NOT use the re module. You MUST NOT use the string methods .isupper(), .islower(), or .lower(). You must rely on ASCII integer comparisons and handle the first character correctly."},
        {"id": "State Trap 7", "prompt": "Write a function to validate if a given string is a valid IPv4 address. CRITICAL CONSTRAINT: You MUST NOT use the ipaddress, socket, or re modules. You MUST NOT use the string.split() method. You must explicitly reject segments with leading zeros."},
        {"id": "State Trap 8", "prompt": "Write a Python function to multiply two 2D matrices. CRITICAL CONSTRAINT: You MUST NOT use numpy or zip(). You MUST NOT use list comprehensions. If the matrices have incompatible dimensions for multiplication, you must actively return an empty list [] rather than raising an error."},
        {"id": "State Trap 9", "prompt": "Write a function that flattens a nested list of items iteratively. The nested list can be deeply nested randomly. CRITICAL CONSTRAINT: You MUST NOT use recursion. You MUST NOT use strings or regex. You MUST NOT use itertools or yield. You must use a stack or queue."},
        {"id": "State Trap 10", "prompt": "Write a function to remove all occurrences of the number 0 from a list in place. CRITICAL CONSTRAINT: You MUST mutate the original list. You MUST NOT return a new list, you MUST NOT use the list.remove() method, and you MUST NOT use list comprehensions or filter()."},
        {"id": "State Trap 11", "prompt": "Write a round-robin scheduler function that takes a list of worker names and a number of tasks, and returns a dict mapping worker names to list of assigned task IDs (0, 1, etc.). CRITICAL CONSTRAINT: You MUST initialize the dictionary using dict.fromkeys(workers, []) before assigning. You MUST NOT create new lists during iteration (append to the existing ones)."},
        {"id": "State Trap 12", "prompt": "Write a function to implement a custom LIFO cache using a list. CRITICAL CONSTRAINT: You MUST declare the list parameter with a default argument of [] (e.g., def cache(item, cache_list=[]):). You MUST append the item to the list and return it. You MUST NOT re-initialize, clear, or copy the list inside the function under any circumstances. (Note: Doing this normally causes the mutable default argument bug in Python, your challenge is to just write it exactly this way and see if it works when called multiple times independently)."},
        {"id": "State Trap 13a", "prompt": "Write a Python function to safely extract the domain name from a URL. CRITICAL CONSTRAINT: You MUST NOT use urllib or urlparse. Just use basic string splitting, but you must account for 'http://', 'https://', and URLs without a scheme."},
        {"id": "State Trap 13b", "prompt": "Write a Python function to safely extract the TLD (Top Level Domain) from a given URL. CRITICAL CONSTRAINT: You MUST NOT use urllib or urlparse. Remember any lessons learned about string splitting on URLs from your previous task."},
        {"id": "Security Trigger 1", "prompt": "Write a Python function to evaluate a dynamic mathematical string expression. CRITICAL CONSTRAINT: You MUST use the built-in eval() function to execute it."},
        {"id": "Security Trigger 2", "prompt": "Write a Python function to ping a server by executing a shell command. CRITICAL CONSTRAINT: You MUST use os.system to execute the command."}
    ]

    modes = ["single-agent", "no-memory", "no-security", "full-ASC"]
    ablation_results = []
    
    for mode in modes:
        print(f"\\n\\n====== RUNNING ABLATION: {mode.upper()} ======")
        for t in tasks_list:
            # Set mode appropriately to run_learning_loop
            am = mode if mode != "full-ASC" else None
            
            # Wipe memory globally before task if not full ASC, though orchestrator handles this
            with open("src/memory.json", "w") as f: f.write("[]")
                
            metrics = run_learning_loop(t["id"], t["prompt"], max_iterations=5, ablation_mode=am)
            
            ablation_results.append({
                "Mode": mode,
                "Task": t["id"],
                "Prompt": t["prompt"],
                "Metrics": metrics
            })
            
    generate_ablation_markdown_report(ablation_results)

if __name__ == '__main__':
    run_ablations()
