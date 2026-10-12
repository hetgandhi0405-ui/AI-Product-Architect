# Cloud Architecture — Hospital Appointment Management

## Purpose
This is a provider-neutral reference architecture for the Hospital Appointment Management System. It identifies common cloud building blocks and the primary request/data flows.

## Diagram files
- `diagrams/cloud-architecture.svg` — rendered diagram suitable for viewing in a browser or inserting into documentation.
- `diagrams/cloud-architecture.mmd` — editable Mermaid source.

## Architecture overview
flowchart LR
  P[Patients and Staff] --> CDN[Secure Web Hosting]
  CDN --> WAF[WAF and Identity / MFA]
  WAF --> LB[Private Application Load Balancer]
  LB --> APP[Appointment Scheduling Service]
  APP --> DB[(Encrypted Managed Database)]
  APP --> CACHE[Managed Cache]
  APP --> Q[Scheduling Event Queue]
  Q --> WORKER[Reminder Worker]
  WORKER --> MSG[SMS / Email Provider]
  APP --> VAULT[Secrets Manager / KMS]
  APP --> AUDIT[Immutable Audit Logs]
  DB --> BACKUP[Encrypted Backups / Recovery]


## Deployment notes
- The diagram is conceptual and does not claim that cloud resources have been provisioned.
- Select a cloud provider and map each provider-neutral block to its managed service before deployment.
- Configure least-privilege access, encryption in transit and at rest, secrets management, observability, backups, and environment-specific network rules.
- Estimate cost and set budgets/alerts before provisioning resources.
