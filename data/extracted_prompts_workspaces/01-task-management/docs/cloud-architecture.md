# Cloud Architecture — Task Management Platform

## Purpose
This is a provider-neutral reference architecture for the Task Management Platform. It identifies common cloud building blocks and the primary request/data flows.

## Diagram files
- `diagrams/cloud-architecture.svg` — rendered diagram suitable for viewing in a browser or inserting into documentation.
- `diagrams/cloud-architecture.mmd` — editable Mermaid source.

## Architecture overview
flowchart LR
  U[Users / Team Members] --> CDN[Cloud CDN]
  CDN --> WEB[Static Web App Hosting]
  WEB --> WAF[WAF and Identity Provider]
  WAF --> LB[Application Load Balancer]
  LB --> APP[Containerized Task Service]
  APP --> CACHE[Managed Cache]
  APP --> DB[(Managed Relational Database)]
  APP --> Q[Managed Queue]
  Q --> WORKER[Background Notification Worker]
  WORKER --> MAIL[Email / Notification Service]
  APP --> OBJ[Object Storage for Attachments]
  APP --> OBS[Logs, Metrics and Traces]
  DB --> BACKUP[Automated Backups]


## Deployment notes
- The diagram is conceptual and does not claim that cloud resources have been provisioned.
- Select a cloud provider and map each provider-neutral block to its managed service before deployment.
- Configure least-privilege access, encryption in transit and at rest, secrets management, observability, backups, and environment-specific network rules.
- Estimate cost and set budgets/alerts before provisioning resources.
