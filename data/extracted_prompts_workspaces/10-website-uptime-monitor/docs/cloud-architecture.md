# Cloud Architecture — Website Uptime Monitoring

## Purpose
This is a provider-neutral reference architecture for the Website Uptime Monitoring Platform. It identifies common cloud building blocks and the primary request/data flows.

## Diagram files
- `diagrams/cloud-architecture.svg` — rendered diagram suitable for viewing in a browser or inserting into documentation.
- `diagrams/cloud-architecture.mmd` — editable Mermaid source.

## Architecture overview
flowchart LR
  U[Users / Operations Team] --> CDN[Dashboard CDN / Hosting]
  CDN --> IDP[Identity and Access]
  IDP --> APP[Monitor Management Service]
  APP --> DB[(Managed Monitor Configuration DB)]
  APP --> Q[Scheduled Check Queue]
  Q --> WORKERS[Distributed Probe Workers]
  WORKERS --> TARGETS[External Websites]
  WORKERS --> RESULTS[Result Ingestion Service]
  RESULTS --> TS[(Time-Series Results Store)]
  RESULTS --> ALERT[Alerting / Incident Service]
  ALERT --> MSG[Email / Chat Notifications]
  APP --> OBS[Logs, Metrics and Traces]


## Deployment notes
- The diagram is conceptual and does not claim that cloud resources have been provisioned.
- Select a cloud provider and map each provider-neutral block to its managed service before deployment.
- Configure least-privilege access, encryption in transit and at rest, secrets management, observability, backups, and environment-specific network rules.
- Estimate cost and set budgets/alerts before provisioning resources.
