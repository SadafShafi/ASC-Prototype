from agents import Manager

def run_learning_loop(task_id, task_prompt, max_iterations=5):
    # Delegate everything to the Manager as it is the orchestrator now
    manager = Manager()
    return manager.orchestrate(task_id, task_prompt, max_iterations)
