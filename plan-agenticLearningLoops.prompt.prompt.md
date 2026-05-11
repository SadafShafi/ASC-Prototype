## Plan: Minimal Multi-Agent Learning Loop Prototype

To prove the core concepts of the paper, we will build a minimal 3-agent society that solves reasoning tasks. The system will demonstrate "learning loops" and "perception/context modeling" by utilizing an episodic memory of past feedback to improve efficiency in subsequent tasks.

**Steps**
1. **Agent Environment Setup**: Initialize a Python environment and standard LLM API connections. Define a simple JSON file to act as the shared *Episodic Memory*.
2. **Implement Roles (Multi-Agent Collaboration)**:
   - `Worker`: Proposes solutions to given tasks.
   - `Critic`: Evaluates the solution and provides a pass/fail along with constructive verbal feedback.
   - `Manager`: Orchestrates communication and extracts actionable rules from the Critic's feedback to store in the Episodic Memory.
3. **Build the Feedback-Driven Learning Loop**: Manager assigns task → Worker attempts → Critic evaluates. If it fails, the feedback is stored. On the next attempt, the Manager injects the memory context so the Worker doesn't repeat mistakes.
4. **Execution Sandbox**: Create a simple script `main.py` to run the society on a predefined set of logic puzzles or mock coding challenges.
5. **Data Evaluation Setup (100% Compliance with Table IV)**: Extract all formal metrics from the execution traces:
   - **CD (Coordination Density)**: Interactions between agents per step.
   - **GAR (Goal Agreement Rate)**: Tracking if the Worker diverges from the prompt.
   - **RSpI (Role Specialization Index)**: Entropy of action types per agent.
   - **RR (Recovery Rate)**: Successes after an initial failure/critique.
   - **SD (Strategy Diversity)**: Variance in code strategies across iterations.
   - **CT (Collective Throughput)**: Iterations needed to successfully finish the task.
   - **BV (Behavioral Variance)**: Stability of actions over time.
   - **FT (Failure Tolerance)**: Success despite induced, simulated agent failures (e.g., Critic going offline).
6. **Knowledge Entropy Consolidation**: Update the Manager to deduplicate and consolidate memory to prevent redundancy.
7. **Governance & Audit**: Implement an immutable `audit_log.json` to record safety, prompts, and policy violations.

**Relevant files**
- `src/agents.py` — The core logic, perception, and decision-making for the Worker, Critic, and Manager.
- `src/memory.json` — The persistent episodic memory structure storing verbal feedback rules.
- `src/audit_log.json` — The governance layer capturing immutable telemetry.
- `src/main.py` — The execution loop integrating the agents.
- `src/benchmark.py` — The testing suite that aggregates the 8 collective-system metrics.

**Verification**
1. Run the system on a generic logic task. The Worker may fail initially, requiring 3-4 loop iterations before the Critic passes it. The pitfalls are saved to memory.
2. Run the system on a similar logic task. The Worker, armed with updated context modeling from the learning loop, should solve it in 1-2 iterations. This objectively proves the architecture's self-evolving capability.

**Decisions**
- Minimal 3-agent setup cleanly hits all domains (Decision-Making, Collaboration, Learning Loops) without overcomplicating the codebase.
- Raw Python with basic API calls is recommended over heavy frameworks (like LangChain) to clearly demonstrate the communication protocol and feedback loops from scratch.

