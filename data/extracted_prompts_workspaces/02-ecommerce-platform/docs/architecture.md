# Architecture — E-Commerce Platform

Browser-based HTML/JavaScript client calls a FastAPI REST service. Pydantic validates payloads. Domain routes operate on in-memory development records. Mermaid source diagrams are in `../diagrams/`.

## Production evolution
Replace the in-memory store with PostgreSQL and migrations; add authentication, authorization, structured logging, rate limiting, and monitoring. Verify diagram-to-code consistency as the system evolves.


## Cloud architecture
See `docs/cloud-architecture.md` and `diagrams/cloud-architecture.svg` for the provider-neutral cloud architecture diagram and editable Mermaid source.
