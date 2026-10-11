# Autonomous AI Product-to-Cloud Platform — Frontend Dashboard

This directory contains the frontend dashboard for the AI-Based Cloud Architecture Generator.

## Architecture

- **React / Vite Application**: Located in `src/App.jsx`, `src/main.jsx`, `src/api.js`, `package.json`, and `vite.config.js`.
- **Standalone Dashboard**: Located in `index.html`. It runs directly without requiring a build step and is served automatically by FastAPI backend at `/`, `/dashboard`, and `/ui`.

## Features

- **Product Requirement Input**: Natural language prompt input with support for custom requirements or 1-click presets (*Task Management App*, *E-Commerce Platform*, *Analytics Dashboard*).
- **Execution Mode Toggle**: Switch between `QUICK` (fast deterministic local synthesis & validation) and `FULL` (deep simulation & LLM inference).
- **Real-Time Pipeline Tracking**: Live progress indicators tracking the entire 20-agent pipeline.
- **Execution Summary**: Project ID, Release Gate status badge, Deployment Readiness badge, and estimated monthly cloud cost.
- **Dynamic Mermaid Cloud Architecture Diagram**: Real-time component flowchart (`flowchart LR`) rendered in dark mode.
- **Cloud Architecture Specification & Infrastructure State**: Inferred compute services, RDS database sizing, Multi-AZ status, Redis cache status, and raw JSON infrastructure state.
- **Unified Product Validation & Testing Report**: Code compilation, API contract test status, database schema validation status.
- **Security & Quality Scores**: Static analysis findings, CORS check, debug flag monitor.
- **Terraform HCL Infrastructure**: List of generated Terraform files and status.
- **Artifact Downloads**: One-click download buttons for Full-Stack Project ZIP and Terraform Infrastructure ZIP.
- **RL-Based Optimization**: Agentic reinforcement learning policy rewards, safety gate status, and fine-tuning dataset record ID.

## Development

To run with Vite dev server:
```bash
npm install
npm run dev
```

To build for production:
```bash
npm run build
```

## Running with Backend

The FastAPI backend automatically serves the integrated dashboard directly:
```bash
uvicorn backend.main:app --reload --port 8000
```
Then navigate to:
- `http://localhost:8000/`
- `http://localhost:8000/dashboard`
