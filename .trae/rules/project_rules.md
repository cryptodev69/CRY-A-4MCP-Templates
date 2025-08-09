## 1. Directory & File Skeleton
my-service/
├── src/
│ └── main.py
├── tests/
│ └── test_main.py
├── requirements.txt # pinned versions
├── pyproject.toml # black/ruff config
├── Dockerfile
├── .gitignore
├── README.md # setup, env vars, run instructions
└── .env.example # placeholder secrets


## 2. Database-Specific Defaults
- **Qdrant**: create `qdrant_client.py` with a `COLLECTION_NAME` constant and a typed `VectorPayload` Pydantic model.  
- **Neo4j**: create `neo4j_client.py` with node labels, relationship types, and a reusable `execute_cypher` helper that always uses parameterized queries.

## 3. Dev-Tooling Boilerplate
- Pre-commit hooks: black, ruff, pytest, pip-audit.  
- GitHub Actions workflow: lint → test → build → push image.  
- Prometheus client wired in `main.py` with a `/metrics` route.

## 4. Environment & Config Management
- Provide a `.env.example` listing every required env var.  
- Use `pydantic-settings` to load and validate env vars at startup.

## 5. Documentation & Onboarding
- README must contain: purpose, quick-start, `make dev`, `make test`, and a link to the API spec (OpenAPI/Swagger).  
- ADR (Architecture Decision Record) stub for any major tech choices.

In case of  Feature Development follow these rules additionally:
**MISSION:** Transform my feature concept into a precise technical specification, then implement only after we both confirm the approach is correct.

**PROTOCOL:**
0. **SILENT SCAN:** Privately identify every missing detail about: user requirements, technical constraints, integration points, performance needs, and acceptance criteria.

1. **CLARIFY LOOP:** ASK one targeted question at a time until you reach ≥95% confidence in delivering the exact feature needed.

2. **ECHO CHECK:** Summarize in one crisp sentence: the feature deliverable, the core user benefit, and the biggest technical challenge.

3. **End with:** "YES to lock" | "EDITS" | "BLUEPRINT" | "RISK" | "WAIT"
   - YES to lock = proceed to implementation
   - EDITS = user wants to modify understanding, return to clarify loop
   - BLUEPRINT = provide detailed technical architecture and implementation plan
   - RISK = identify potential technical risks and edge cases
   - WAIT = pause process, user needs time to decide

4. **BUILD & SELF-TEST:** Implement feature with tests, validate against requirements, check for edge cases and integration issues. Fix before delivery.

5. **RESET:** Restart the process if scope changes.