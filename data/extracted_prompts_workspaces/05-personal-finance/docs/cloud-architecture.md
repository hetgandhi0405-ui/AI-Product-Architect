# Cloud Architecture — Personal Finance Tracker

## Purpose
This is a provider-neutral reference architecture for the Personal Finance Tracker. It identifies common cloud building blocks and the primary request/data flows.

## Diagram files
- `diagrams/cloud-architecture.svg` — rendered diagram suitable for viewing in a browser or inserting into documentation.
- `diagrams/cloud-architecture.mmd` — editable Mermaid source.

## Architecture overview
flowchart LR
  U[Users] --> CDN[CDN / Frontend Hosting]
  CDN --> WAF[WAF and Identity / MFA]
  WAF --> LB[Application Load Balancer]
  LB --> APP[Finance Application Service]
  APP --> DB[(Encrypted Transaction Database)]
  APP --> CACHE[Managed Cache]
  APP --> Q[Import / Report Queue]
  Q --> WORKER[Statement and Budget Worker]
  WORKER --> OBJ[Private Document Storage]
  APP --> KMS[Key Management Service]
  APP --> AUDIT[Security Audit Logs]
  DB --> BACKUP[Encrypted Backups]


## Deployment notes
- The diagram is conceptual and does not claim that cloud resources have been provisioned.
- Select a cloud provider and map each provider-neutral block to its managed service before deployment.
- Configure least-privilege access, encryption in transit and at rest, secrets management, observability, backups, and environment-specific network rules.
- Estimate cost and set budgets/alerts before provisioning resources.
