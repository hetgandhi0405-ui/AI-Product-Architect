# Security Notes — Student Learning Management System

- Development-only; endpoints are unauthenticated.
- CORS is permissive for local testing and must be restricted before deployment.
- In-memory data is not durable.
- Use synthetic data only; do not enter sensitive personal, medical, or financial data.
- Add authentication, authorization, rate limiting, audit logging, secrets management, and dependency scans before production.
