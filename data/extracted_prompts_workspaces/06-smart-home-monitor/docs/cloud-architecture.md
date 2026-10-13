# Cloud Architecture — Smart Home Monitoring

## Purpose
This is a provider-neutral reference architecture for the Smart Home Monitoring Dashboard. It identifies common cloud building blocks and the primary request/data flows.

## Diagram files
- `diagrams/cloud-architecture.svg` — rendered diagram suitable for viewing in a browser or inserting into documentation.
- `diagrams/cloud-architecture.mmd` — editable Mermaid source.

## Architecture overview
flowchart LR
  D[IoT Devices and Sensors] --> GW[Home IoT Gateway]
  GW --> IOT[Managed IoT Device Broker]
  IOT --> RULES[Device Registry and Rules Engine]
  RULES --> STREAM[Managed Event Stream]
  STREAM --> PROC[Telemetry Processing Service]
  PROC --> TS[(Time-Series Database)]
  PROC --> ALERT[Alert / Notification Service]
  ALERT --> U[Mobile / Web Dashboard]
  U --> IDP[Identity and Device Permissions]
  U --> API[Device Management Service]
  API --> IOT
  PROC --> OBS[Monitoring and Logs]


## Deployment notes
- The diagram is conceptual and does not claim that cloud resources have been provisioned.
- Select a cloud provider and map each provider-neutral block to its managed service before deployment.
- Configure least-privilege access, encryption in transit and at rest, secrets management, observability, backups, and environment-specific network rules.
- Estimate cost and set budgets/alerts before provisioning resources.
