# Repository Analysis — Deliverymap US-Dev CD Pipeline

## Repository Overview

This is a **sanitized snapshot** of an **Azure DevOps (ADO) Continuous Deployment (CD) pipeline** for the **PwC Concourse** platform — a large microservices-based application deployed to **Azure Kubernetes Service (AKS)**. Sensitive values (secrets, URLs, IDs) have been replaced with `"sanitized"` for safe sharing.

---

## Structure & Key Files

### 1. 🚀 Pipeline Entry Point — `ConcourseCore/deploy/monorepo-targeted-deploy-with-secrets.yaml`

**This is where the pipeline starts.** It's an Azure DevOps YAML pipeline (`trigger: none` — manually triggered) that deploys **~19 microservices** to Kubernetes in a single run. Key aspects:

- **Parameters** (lines 4–196): Accepts the target `ENVIRONMENT` (e.g. `us-dev`, `us-prod`, `emea-prod`), a list of `service` objects (each with a name, build ID, and config branches), plus toggles like `promoteFromDev` and `RESTART_PODS`.
- **Resources** (lines 214–226): Checks out 3 repos:
  - **ConcourseCore** (self) — K8s manifests & config
  - **tech-enablement** (GitHub) — app config (`docker.k8.yml`)
  - **administration** — helper scripts
- **Deploy stage** (lines 228–624): Iterates over every service in `${{ each service in parameters.service }}` and for each one executes the workflow below.

#### Per-Service Deployment Steps

| Step | What it does |
|---|---|
| Checkout repos | Clones ConcourseCore, tech-enablement, and administration |
| Set branch targets | Determines which config branches to use per service |
| Replace Tokens | Uses the `replacetokens` ADO task to substitute `<{VARIABLE}>` placeholders in K8s manifests with pipeline variable values |
| Create YAML ConfigMap | Appends the full `docker.k8.yml` content into a K8s ConfigMap and deploys it |
| Get Secrets Names | Runs `get-secrets-from-yaml.py` to parse the deployment YAML and extract which secrets each service needs |
| Fetch AKV Secrets | Uses `az keyvault secret show` to pull each secret from Azure Key Vault |
| Bake Secret Map | Runs `bake-secretmap.sh` to generate a Kustomize `secretGenerator` manifest, then bakes it via `KubernetesManifest@1` |
| Deploy to K8s | Applies the **Secret**, **Deployment**, **Service**, and conditionally the **HPA** manifests to AKS |
| WayDev metadata | POSTs deployment metadata to WayDev for tracking |

---

### 2. ☸️ Kubernetes Manifests — `ConcourseCore/k8s/`

- **`concourse-deliverymap-svc/deployment.yaml`** — The actual K8s `Deployment` for the deliverymap service. Features init containers for **Liquibase** DB migrations (MongoDB), Datadog APM sidecar labels, liveness/readiness probes, and templated `<{VARIABLE}>` placeholders.
- **`concourse-deliverymap-svc/hpa.yaml`** — Horizontal Pod Autoscaler: scales 5–20 pods based on 60% memory utilization.
- **`concourse-deliverymap-svc/configs/us-dev/...configmap.yaml`** — Environment-specific K8s ConfigMap for `us-dev` (MongoDB, Redis, Azure Blob, Datadog settings, etc.).
- **`microservice-template/`** — Generic **template** Deployment and Service manifests copied for any service that doesn't have its own custom ones.

---

### 3. ⚙️ Application Configuration — `tech-enablement/config/docker.k8.yml`

A massive (~1514 lines) YAML file containing the **full application configuration** for all microservices — organized under `GLOBAL_CONFIG` and per-service sections. Includes:

- Auth (OpenAM, Azure AD), GUM user management
- MongoDB, Redis, Azure Service Bus, EventHub connections
- LDAP, Jira, Miro, SharePoint integrations
- Feature flags, logging, storage, and more

This file gets injected into a Kubernetes ConfigMap as `config.yaml` during deployment.

---

### 4. 🔧 Administration Scripts — `administration/scripts/`

- **`bake-secretmap.sh`** — Generates a Kustomize `kustomization.yaml` with a `secretGenerator` referencing individual secret files pulled from Azure Key Vault.
- **`get-secrets-from-yaml.py`** — Parses a K8s deployment YAML to find all `secretKeyRef` entries, extracts their key names, converts them to camelCase, and outputs them as an ADO pipeline variable (`APP_SECRETS`) for downstream secret-fetching steps.
- **`requirements.txt`** — Python dependencies: `click` and `PyYAML`.

---

## Pipeline Flow Diagram

```
Manual Trigger (Azure DevOps)
       │
       ▼
┌──────────────────────────────────────┐
│  monorepo-targeted-deploy-with-      │
│  secrets.yaml                        │
│  (for each of ~19 microservices)     │
└──────────────┬───────────────────────┘
               │
    ┌──────────▼──────────┐
    │  Checkout 3 repos   │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │  Token replacement  │  ← Fills <{VAR}> placeholders
    │  in K8s manifests   │    in deployment.yaml, hpa.yaml, etc.
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │  Build ConfigMap     │  ← K8s ConfigMap + docker.k8.yml
    │  Deploy to AKS       │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │  Extract secret      │  ← get-secrets-from-yaml.py
    │  names from YAML     │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │  Fetch secrets from  │  ← az keyvault secret show
    │  Azure Key Vault     │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │  Bake & deploy       │  ← bake-secretmap.sh + Kustomize
    │  K8s Secrets         │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │  Deploy Deployment,  │  ← KubernetesManifest@1
    │  Service, HPA to AKS │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │  Post WayDev         │  ← Deployment tracking
    │  metadata            │
    └──────────────────────┘
```

---

## Deployed Microservices (~19)

| Service Name | Short Name | Context Path |
|---|---|---|
| concourse-appintegrations-mgmt-svc | appintegrationsmgmt | appintegrations-mgmt |
| concourse-auth-svc | auth | auth |
| concourse-chat-svc | chat | chat |
| concourse-deliverables-svc | deliverables | deliverables |
| concourse-deliverymap-svc | deliverymap | deliverymap |
| concourse-digital-assets-svc | digitalAssets | digitalAssets |
| concourse-engagement-svc | engagement | engagement |
| concourse-integration-ipaas-svc | ipaas | ipaas |
| concourse-integration-jira-svc | jira | jira |
| concourse-integration-miro-svc | integrationmiro | miro-integration |
| concourse-integration-ms365-sharepoint-svc | ms365 | ms365-sharepoint |
| concourse-integration-pwcinternal-svc | integrationpwcinternal | pwcinternal |
| concourse-integration-provision-svc | integrationprovision | provision |
| concourse-notification-svc | notification | notification |
| concourse-pursuit-scope-svc | pursuitscope | pursuit-scope |
| concourse-raid-svc | raid | raid |
| concourse-reports-svc | reports | reports |
| concourse-user-profile-svc | user | user-profile |
| concourse-estimation-models-svc | estimationmodels | estimation-models |

---

## Key Technologies

- **CI/CD:** Azure DevOps Pipelines (YAML)
- **Container Orchestration:** Kubernetes (AKS)
- **Secrets Management:** Azure Key Vault → Kustomize secretGenerator
- **Config Management:** K8s ConfigMaps + token replacement (`replacetokens` ADO task)
- **Database Migrations:** Liquibase (init containers)
- **Monitoring:** Datadog APM (labels + tracing)
- **Autoscaling:** Kubernetes HPA (memory-based, 5–20 replicas)
- **Deployment Tracking:** WayDev API

---

## Summary

The pipeline starts at `ConcourseCore/deploy/monorepo-targeted-deploy-with-secrets.yaml`, loops over every microservice, hydrates templated K8s manifests with variables and secrets, and deploys everything to AKS in the selected environment.
