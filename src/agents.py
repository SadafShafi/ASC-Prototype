import os
import json
import random
import datetime
import math
import re
from collections import Counter
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL = os.getenv("MODEL", "meta-llama-3.1-8b-instruct")

# Initialize the OpenAI compatible client
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

def log_audit(action_type, agent, details):
    """Immutable Governance Audit Log"""
    entry = {
        "timestamp": str(datetime.datetime.now()),
        "agent": agent,
        "action_type": action_type,
        "details": details
    }
    with open("src/audit_log.json", "a") as f:
        f.write(json.dumps(entry) + "\n")

def call_llm(system_prompt, user_prompt, temperature=0.2, timeout=15.0):
    """Utility function to make calls to the LLM."""
    print(f"      [DEBUG] Making LLM call (timeout={timeout}s)...")
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            timeout=timeout
        )
        print("      [DEBUG] LLM call returned successfully.")
        return response.choices[0].message.content
    except Exception as e:
        print(f"\n[NETWORK TIMEOUT or API ERROR] LLM call failed: {str(e)}")
        raise e

class Worker:
    def __init__(self):
        self.system_prompt = (
            "You are a Worker agent. Solve the task considering historical feedback.\n"
            "Format your response exactly as:\n"
            "STRATEGY: <Name of your algorithm/approach>\n"
            "SOLUTION: <Your Python code>"
        )

    def solve(self, task, memory_context):
        user_prompt = f"Task: {task}\n\nMemory:\n{memory_context}\n\nResponse:"
        res = call_llm(self.system_prompt, user_prompt)
        log_audit("PROPOSE_SOLUTION", "Worker", {"task": task, "response_snippet": res[:50].replace('\n', ' ')})
        return res

class Critic:
    def __init__(self):
        self.system_prompt = (
            "You are a Critic agent. Evaluate the solution.\n"
            "Format exactly as:\n"
            "DECISION: PASS or FAIL\n"
            "FEEDBACK: <Critique>"
        )

    def evaluate(self, task, solution):
        if random.random() < 0.10:
            log_audit("CRITIC_OFFLINE", "Critic", {"task": task})
            raise ConnectionError("Critic service temporarily offline (Simulated FT)")

        user_prompt = f"Task: {task}\n\nSolution:\n{solution}\n\nEvaluate:"
        try:
            res = call_llm(self.system_prompt, user_prompt)
            lines = res.strip().split('\n', 1)
            decision = lines[0].upper()
            feedback = lines[1].replace("FEEDBACK:", "").strip() if len(lines) > 1 else res
            passed = "PASS" in decision and "FAIL" not in decision
            log_audit("EVALUATE", "Critic", {"passed": passed})
            return {"passed": passed, "feedback": feedback}
        except Exception as e:
            return {"passed": False, "feedback": f"Critic parsing error: {str(e)}"}

class SecurityFilter:
    """Security Filtering (Algorithm 2 Audit Gate)"""
    def __init__(self):
        self.forbidden_patterns = ["os.system", "subprocess", "eval(", "exec(", "rm -rf"]
        
    def check_safety(self, solution):
        for pattern in self.forbidden_patterns:
            if pattern in solution:
                log_audit("SAFETY_VIOLATION", "SecurityFilter", {"pattern": pattern})
                return False, f"Safety violation: Disallowed pattern '{pattern}' detected."
        
        log_audit("SAFETY_PASS", "SecurityFilter", {})
        return True, "Safe"

class Manager:
    """Orchestrates communication dynamically and manages the episodic memory."""
    def __init__(self, memory_file="src/memory.json"):
        self.memory_file = memory_file
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, 'w') as f:
                json.dump([], f)
        if not os.path.exists("src/audit_log.json"):
            with open("src/audit_log.json", 'w') as f:
                f.write("")
                
        self.worker = Worker()
        self.critic = Critic()
        self.security = SecurityFilter()

    def load_memory(self):
        with open(self.memory_file, 'r') as f:
            return json.load(f)

    def update_memory(self, task, new_feedback):
        memory = self.load_memory()
        if len(memory) > 0:
            prompt = (
                f"Consolidate this new feedback: '{new_feedback}' with existing memory: '{str(memory)}'. "
                "Output ONLY a JSON array of concise, unique rules strings. Do not use markdown."
            )
            try:
                consolidated_str = call_llm("You are a memory optimizer. Return valid JSON array.", prompt)
                clean_str = consolidated_str.replace("```json", "").replace("```", "").strip()
                updated_memory = json.loads(clean_str)
            except:
                updated_memory = memory + [new_feedback]
        else:
            updated_memory = [{"task": task, "lesson_learned": new_feedback}]

        with open(self.memory_file, 'w') as f:
            json.dump(updated_memory, f, indent=2)
            
        log_audit("CONSOLIDATE_MEMORY", "Manager", {"new_rules_count": len(updated_memory)})

    def get_memory_context(self):
        memory = self.load_memory()
        if not memory: return "No prior memory."
        return "\n".join([f"[{i+1}] {e.get('lesson_learned', '') if isinstance(e, dict) else e}" for i, e in enumerate(memory)])

    def determine_next_node(self, current_state):
        """Dynamic Routing Topology: The manager routes dynamically based on constraints, rather than a hard loop."""
        if current_state["status"] == "start" or current_state["status"] == "needs_rework":
            return "worker"
        elif current_state["status"] == "solution_generated":
            return "security"
        elif current_state["status"] == "security_passed":
            return "critic"
        elif current_state["status"] == "approved":
            return "end"
        return "end"

    def orchestrate(self, task_id, task_prompt, max_iterations=5):
        print(f"\n========== Starting Task {task_id} ==========")
        
        iteration = 0
        cd_count = 0 
        strategies_used = set()
        valid_goal_steps = 0
        failures_tolerated = 0
        solution_lengths = []
        
        state = {"status": "start", "solution": None, "feedback": None}
        passed = False
        trajectory = []
        
        while iteration < max_iterations and state["status"] != "end":
            next_node = self.determine_next_node(state)
            
            if next_node == "worker":
                iteration += 1
                if iteration > max_iterations: break
                print(f"\n--- [Iteration {iteration}] ---")
                
                print(">> Manager dynamically routing to Worker...")
                state["solution"] = self.worker.solve(task_prompt, self.get_memory_context())
                cd_count += 1
                solution_lengths.append(len(state["solution"]))
                
                if "STRATEGY:" in state["solution"] and "SOLUTION:" in state["solution"]:
                    valid_goal_steps += 1
                    
                match = re.search(r'STRATEGY:\s*(.*?)\n', state["solution"], re.IGNORECASE)
                strategy = match.group(1).strip() if match else "Unknown strategy"
                strategies_used.add(strategy)
                state["status"] = "solution_generated"
                
                # Setup current trajectory step
                trajectory.append({"iteration": iteration, "strategy": strategy, "solution": state["solution"], "security": "Pending", "critic": "Pending", "feedback": ""})
                
            elif next_node == "security":
                print(">> Manager dynamically routing to SecurityFilter (Evaluation Gate)...")
                is_safe, sec_feedback = self.security.check_safety(state["solution"])
                cd_count += 1
                if is_safe:
                    trajectory[-1]["security"] = "PASS"
                    state["status"] = "security_passed"
                else:
                    print(f"❌ Security Block! {sec_feedback}")
                    trajectory[-1]["security"] = f"FAIL: {sec_feedback}"
                    trajectory[-1]["critic"] = "SKIPPED"
                    state["feedback"] = sec_feedback
                    state["status"] = "needs_rework"
                    
            elif next_node == "critic":
                print(">> Manager dynamically routing to Critic...")
                try:
                    evaluation = self.critic.evaluate(task_prompt, state["solution"])
                    cd_count += 1
                    feedback = evaluation.get("feedback", "No feedback.")
                    trajectory[-1]["feedback"] = feedback
                    
                    if evaluation.get("passed", False):
                        trajectory[-1]["critic"] = "PASS"
                        state["status"] = "end"
                        passed = True
                    else:
                        print("❌ Critic failed. Memory updated.")
                        trajectory[-1]["critic"] = "FAIL"
                        self.update_memory(task_prompt, feedback)
                        cd_count += 1
                        state["status"] = "needs_rework"
                except ConnectionError as e:
                    print(f"[!] {str(e)} -> Simulating FT by retrying...")
                    failures_tolerated += 1
                    
            elif next_node == "end":
                break
                
        # Metric Calculations...

        recovered = (iteration > 1 and passed)
        gar = valid_goal_steps / iteration if iteration > 0 else 0.0
        sd = len(strategies_used)
        rspi = 0.0
        bv = 0.0
        
        # Calculate RSpI
        try:
            with open("src/audit_log.json", "r") as f:
                logs = [json.loads(line) for line in f if line.strip()]
            agent_actions = {}
            for log in logs:
                agent_actions.setdefault(log["agent"], []).append(log["action_type"])
            entropy_sum = 0
            for acts in agent_actions.values():
                counts = Counter(acts)
                total = sum(counts.values())
                entropy_sum += -sum((c/total) * math.log2(c/total) for c in counts.values())
            rspi = entropy_sum / len(agent_actions) if agent_actions else 0.0
        except Exception: pass
            
        # Calculate BV
        if len(solution_lengths) > 1:
            mean = sum(solution_lengths) / len(solution_lengths)
            variance = sum((x - mean) ** 2 for x in solution_lengths) / len(solution_lengths)
            bv = math.sqrt(variance)
            
        print(f"{'✅ Task completed successfully!' if passed else '❌ Task aborted.'}")
        return {
            "CT": iteration, "CD": cd_count, "GAR": gar, "RSpI": rspi,
            "SD": sd, "BV": bv, "FT": failures_tolerated, "RR": recovered,
            "Task_Passed": passed,
            "Trajectory": trajectory
        }
