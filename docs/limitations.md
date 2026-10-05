# System Limitations & Future Improvements

## Current Limitations

1. **Test-Driven Oracle Dependency:**
   - The autonomous self-healing loop requires executable automated tests (Jest, Pytest, etc.) as the validation oracle. If a project has zero tests, Scout will report zero failures, requiring manual test synthesis.

2. **Language Support Scope:**
   - Initial reliable out-of-the-box support is verified for **TypeScript**, **JavaScript**, and **Python**.
   - Java (Maven / JUnit) architecture is planned and stubbed in project type detection, but full enterprise build chains require Maven daemon containers.

3. **Multi-Repository Monorepos:**
   - The current workspace model assumes a single microservice root or standalone repository. Highly nested polyglot monorepos requiring inter-package builds are not yet natively orchestrated.

4. **Maximum Iteration Bound:**
   - `MAX_ITERATIONS` is capped at 5 to prevent unbounded LLM token consumption and infinite loops. Highly complex architectural refactors requiring >5 steps will trigger `HUMAN_INTERVENTION_REQUIRED`.

---

## Future Improvements

1. **Automated Test Generation Agent:**
   - Introduce an auxiliary agent to synthesize regression tests for repositories lacking test suites.

2. **Multi-Model LLM Routing:**
   - Route lightweight code search tasks to smaller models (e.g. Gemini Flash) and complex multi-file architectural reasoning to frontier reasoning models.

3. **Semantic Code Embeddings:**
   - Integrate vector code search (e.g. tree-sitter AST embeddings) to trace deeply nested dependency graphs across large enterprise codebases.
