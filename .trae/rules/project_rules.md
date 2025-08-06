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