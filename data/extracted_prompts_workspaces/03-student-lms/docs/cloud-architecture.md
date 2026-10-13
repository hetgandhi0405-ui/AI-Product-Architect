# Cloud Architecture — Student Learning Management System

## Purpose
This is a provider-neutral reference architecture for the Student Learning Management System. It identifies common cloud building blocks and the primary request/data flows.

## Diagram files
- `diagrams/cloud-architecture.svg` — rendered diagram suitable for viewing in a browser or inserting into documentation.
- `diagrams/cloud-architecture.mmd` — editable Mermaid source.

## Architecture overview
flowchart LR
  S[Students and Instructors] --> CDN[CDN / Web Hosting]
  CDN --> IDP[Identity and Access Management]
  IDP --> LB[Application Load Balancer]
  LB --> APP[LMS Application Services]
  APP --> DB[(Managed Course / Enrollment DB)]
  APP --> MEDIA[Object Storage for Learning Media]
  MEDIA --> CDN
  APP --> Q[Assignment Processing Queue]
  Q --> WORKER[Grading / Notification Workers]
  WORKER --> MSG[Email / Learning Notifications]
  APP --> CACHE[Managed Cache]
  APP --> OBS[Monitoring and Audit Logs]
  DB --> BACKUP[Backups and Recovery]


## Deployment notes
- The diagram is conceptual and does not claim that cloud resources have been provisioned.
- Select a cloud provider and map each provider-neutral block to its managed service before deployment.
- Configure least-privilege access, encryption in transit and at rest, secrets management, observability, backups, and environment-specific network rules.
- Estimate cost and set budgets/alerts before provisioning resources.
