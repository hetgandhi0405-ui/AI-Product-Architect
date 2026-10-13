# Cloud Architecture — Employee Attendance Management

## Purpose
This is a provider-neutral reference architecture for the Employee Attendance Management System. It identifies common cloud building blocks and the primary request/data flows.

## Diagram files
- `diagrams/cloud-architecture.svg` — rendered diagram suitable for viewing in a browser or inserting into documentation.
- `diagrams/cloud-architecture.mmd` — editable Mermaid source.

## Architecture overview
flowchart LR
  E[Employees and HR] --> CDN[Secure Web Hosting]
  CDN --> IDP[SSO / Identity Provider]
  IDP --> LB[Application Load Balancer]
  LB --> APP[Attendance and Leave Service]
  APP --> DB[(Managed HR Database)]
  APP --> Q[Timesheet / Leave Event Queue]
  Q --> WORKER[Policy and Payroll Export Worker]
  WORKER --> PAY[Payroll / HR Integrations]
  APP --> OBJ[Private Document Storage]
  APP --> AUDIT[Audit Logs]
  DB --> BACKUP[Backup and Recovery]


## Deployment notes
- The diagram is conceptual and does not claim that cloud resources have been provisioned.
- Select a cloud provider and map each provider-neutral block to its managed service before deployment.
- Configure least-privilege access, encryption in transit and at rest, secrets management, observability, backups, and environment-specific network rules.
- Estimate cost and set budgets/alerts before provisioning resources.
