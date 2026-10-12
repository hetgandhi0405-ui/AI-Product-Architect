# Cloud Architecture — Real-Time Analytics Dashboard

## Purpose
This is a provider-neutral reference architecture for the Real-Time Analytics Dashboard. It identifies common cloud building blocks and the primary request/data flows.

## Diagram files
- `diagrams/cloud-architecture.svg` — rendered diagram suitable for viewing in a browser or inserting into documentation.
- `diagrams/cloud-architecture.mmd` — editable Mermaid source.

## Architecture overview
flowchart LR
  SRC[Web / App Event Producers] --> ING[Event Ingestion Gateway]
  ING --> STREAM[Managed Event Streaming]
  STREAM --> PROC[Stream Processing Jobs]
  PROC --> HOT[(Low-Latency Analytics Store)]
  PROC --> LAKE[(Object Storage Data Lake)]
  LAKE --> ETL[Batch ETL / Warehouse Loads]
  ETL --> WH[(Cloud Data Warehouse)]
  HOT --> API[Dashboard Query Service]
  WH --> API
  API --> CDN[Dashboard Web Hosting / CDN]
  CDN --> U[Analysts and Product Teams]
  ING --> OBS[Monitoring / Dead-Letter Queue]


## Deployment notes
- The diagram is conceptual and does not claim that cloud resources have been provisioned.
- Select a cloud provider and map each provider-neutral block to its managed service before deployment.
- Configure least-privilege access, encryption in transit and at rest, secrets management, observability, backups, and environment-specific network rules.
- Estimate cost and set budgets/alerts before provisioning resources.
