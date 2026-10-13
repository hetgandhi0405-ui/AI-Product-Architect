# Cloud Architecture — Customer Support Ticketing

## Purpose
This is a provider-neutral reference architecture for the Customer Support Ticketing System. It identifies common cloud building blocks and the primary request/data flows.

## Diagram files
- `diagrams/cloud-architecture.svg` — rendered diagram suitable for viewing in a browser or inserting into documentation.
- `diagrams/cloud-architecture.mmd` — editable Mermaid source.

## Architecture overview
flowchart LR
  C[Customers and Agents] --> CDN[Web App Hosting / CDN]
  CDN --> WAF[WAF and Identity Provider]
  WAF --> LB[Application Load Balancer]
  LB --> APP[Ticketing Application]
  APP --> DB[(Managed Ticket Database)]
  APP --> SEARCH[Managed Search Index]
  APP --> Q[Ticket Event Queue]
  Q --> WORKER[Assignment / SLA Worker]
  WORKER --> MSG[Email / In-App Notifications]
  APP --> OBJ[Private Attachment Storage]
  APP --> OBS[Audit Logs and Monitoring]


## Deployment notes
- The diagram is conceptual and does not claim that cloud resources have been provisioned.
- Select a cloud provider and map each provider-neutral block to its managed service before deployment.
- Configure least-privilege access, encryption in transit and at rest, secrets management, observability, backups, and environment-specific network rules.
- Estimate cost and set budgets/alerts before provisioning resources.
