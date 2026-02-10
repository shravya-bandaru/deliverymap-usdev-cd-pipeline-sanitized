# ADO → GitHub Actions Migration Mapping

This document provides a comprehensive mapping between the original Azure DevOps (ADO) pipeline and the converted GitHub Actions workflow.

---

## Trigger & Parameters

| ADO | GitHub Actions | Notes |
|---|---|---|
| `trigger: none` | `on: workflow_dispatch` | Both are manual-only triggers |
| `parameters:` with `values:` | `inputs:` with `type: choice` + `options:` | GHA dropdown equivalent |
| `parameters:` with `type: boolean` | `inputs:` with `type: boolean` | Direct mapping |
| `parameters:` with `type: object` (service list) | `services.json` + matrix strategy | GHA has no native object parameter; use JSON file + `fromJson()` |

---

## Variables & Secrets

| ADO | GitHub Actions | Notes |
|---|---|---|
| `variables: - group: ConcourseCore` | GitHub Actions **org/repo secrets** | Migrate variable group values to GHA secrets |
| `variables: - group: ${{ parameters.ENVIRONMENT }}` | **GitHub Environments** (per env secrets/vars) | Create a GHA Environment per region (us-dev, us-prod, etc.) |
| `$(VARIABLE_NAME)` (runtime) | `${{ env.VARIABLE_NAME }}` or `$VARIABLE_NAME` | Runtime variable access |
| `${{ parameters.X }}` (compile-time) | `${{ inputs.X }}` | Compile-time → dispatch input |
| `##vso[task.setvariable variable=X]val` | `echo "X=val" >> "$GITHUB_ENV"` | Set variable for subsequent steps |
| `##vso[task.setvariable variable=X;isOutput=true]` | `echo "X=val" >> "$GITHUB_OUTPUT"` | Set output for use in other jobs |
| `##vso[build.updatebuildnumber]` | No direct equivalent | GHA run numbers are immutable |
| `$[lower(replace(...))]` (ADO expression) | Bash: `echo "$VAR" \| tr '[:upper:]' '[:lower:]' \| tr '.' '-'` | ADO expressions replaced with shell logic |

---

## Service Iteration

| ADO | GitHub Actions | Notes |
|---|---|---|
| `${{ each service in parameters.service }}:` | `strategy: matrix` with `fromJson()` | Services defined in `services.json` |
| `${{ service.name }}` | `${{ matrix.service.name }}` | Matrix context replaces `each` loop context |
| `${{ service.buildId }}` | `${{ matrix.service.buildId }}` | Same pattern for all service properties |
| `fail-fast: false` implicit | `fail-fast: false` explicit | Ensure one service failure doesn't cancel others |
| Sequential deployment jobs | `max-parallel: 5` | Configurable concurrency |

---

## Repository Checkout

| ADO | GitHub Actions | Notes |
|---|---|---|
| `checkout: self` | `actions/checkout@v4` (default) | Self repo checkout |
| `checkout: microserviceConfig` (external GitHub repo) | `actions/checkout@v4` with `repository:` + `token:` | Requires a PAT (`TECH_ENABLEMENT_PAT` secret) |
| `checkout: administration` (ADO repo) | `actions/checkout@v4` with `repository:` + `token:` | Requires a PAT (`ADMIN_REPO_PAT` secret) |
| `persistCredentials: true` | Not needed (GHA handles token automatically) | — |

---

## Tasks & Steps

| ADO Task | GitHub Actions Equivalent | Notes |
|---|---|---|
| `script:` / `bash:` | `run:` (shell: bash is default on ubuntu) | Direct mapping |
| `displayName:` | `name:` (step name) | Step labelling |
| `condition: and(succeeded(), eq(...))` | `if: ${{ ... }}` | Expression syntax differs |
| `condition: always()` | `if: always()` | Direct mapping |
| `workingDirectory:` | `working-directory:` | Hyphenated in GHA |

---

## Azure & Kubernetes Tasks

| ADO Task | GitHub Actions Equivalent | Notes |
|---|---|---|
| `AzureCLI@2` with `azureSubscription` | `azure/login@v2` (OIDC) + inline `az` commands | Uses federated credentials (client-id, tenant-id, subscription-id) |
| `KubernetesManifest@1` (action: deploy) | `kubectl apply -f <manifest>` | Requires `azure/aks-set-context@v4` first |
| `KubernetesManifest@1` (action: bake, kustomize) | `kubectl kustomize <path>` | Native kustomize in kubectl |
| `Kubernetes@1` (rollout restart) | `kubectl rollout restart deployment <name>` | Direct CLI equivalent |
| `$(K8S_SERVICE_CONNECTION)` | `azure/aks-set-context@v4` with `cluster-name` + `resource-group` | Service connection → AKS context action |
| `$(AZURE_SERVICE_CONNECTION)` | `azure/login@v2` secrets | Service principal or OIDC workload identity |

---

## Token Replacement

| ADO Task | GitHub Actions Equivalent | Notes |
|---|---|---|
| `qetza.replacetokens@6` with `tokenPrefix: <{` / `tokenSuffix: }>` | `scripts/replace-tokens.py` (custom) | Reads env vars, replaces `<{VAR}>` tokens in files |
| `actionOnMissing: warn` | Script prints `[WARN]` and uses `defaultValue` | Same behavior |
| `defaultValue: defaultValue` | `DEFAULT_VALUE` env var (defaults to `"defaultValue"`) | Configurable |

---

## Secrets Management

| ADO | GitHub Actions | Notes |
|---|---|---|
| `az keyvault secret show` in `AzureCLI@2` | `az keyvault secret show` after `azure/login@v2` | Same CLI, different auth mechanism |
| `$(AZ_KEY_VAULT)` from variable group | `${{ secrets.AZ_KEY_VAULT }}` | Stored in GHA Environment secrets |
| `$(bake.manifestsBundle)` output | `kubectl kustomize > file.yaml` | Direct file output instead of task output variable |

---

## ADO Built-in Variables → GHA Equivalents

| ADO Variable | GitHub Actions Equivalent |
|---|---|
| `$(Build.BuildId)` | `${{ github.run_id }}` |
| `$(Build.SourceBranchName)` | `${{ github.ref_name }}` |
| `$(Agent.JobStatus)` | `${{ job.status }}` |
| `$(System.DefaultWorkingDirectory)` | `${{ github.workspace }}` |
| `$(Pipeline.Workspace)/s/` | `${{ github.workspace }}/` |
| `$(Build.SourcesDirectory)` | `${{ github.workspace }}` |

---

## Conditional Logic

| ADO Pattern | GitHub Actions Pattern |
|---|---|
| `${{ if in(parameters.ENVIRONMENT, 'us-stage', 'us-prod', ...) }}` | `if: contains(fromJson('["us-stage","us-prod",...]'), inputs.ENVIRONMENT)` |
| `${{ if and(in(...), in(...)) }}` | `if: contains(...) && contains(...)` |
| `condition: eq(variables['X'], 'true')` | `if: env.X == 'true'` or `if: inputs.X == true` |
| `condition: or(eq(...), eq(...))` | `if: env.X == 'a' \|\| env.X == 'b'` |

---

## Required GitHub Secrets (per Environment)

These must be configured in **GitHub repo → Settings → Environments → [env-name] → Secrets**:

| Secret Name | Purpose | ADO Equivalent |
|---|---|---|
| `AZURE_CLIENT_ID` | Azure OIDC login | `$(AZURE_SERVICE_CONNECTION)` service principal |
| `AZURE_TENANT_ID` | Azure OIDC login | Embedded in service connection |
| `AZURE_SUBSCRIPTION_ID` | Azure OIDC login | Embedded in service connection |
| `AKS_CLUSTER_NAME` | AKS cluster target | `$(K8S_SERVICE_CONNECTION)` |
| `AKS_RESOURCE_GROUP` | AKS resource group | `$(K8S_SERVICE_CONNECTION)` |
| `AZ_KEY_VAULT` | Key Vault name | `$(AZ_KEY_VAULT)` from variable group |
| `TECH_ENABLEMENT_PAT` | Cross-repo checkout (GitHub) | `endpoint: pwc-us-adv-tech-enablement` |
| `ADMIN_REPO_PAT` | Cross-repo checkout | ADO `repository: administration` |
| `WAYDEV_API_HOST` | Deployment tracking endpoint | `$(WAYDEV_API_HOST)` from variable group |
| `WAYDEV_API_KEY` | Deployment tracking auth | `$(WAYDEV_API_KEY)` from variable group |

---

## File Structure Mapping

```
ADO (original)                              GitHub Actions (converted)
─────────────────────────────────────       ──────────────────────────────────────
ConcourseCore/deploy/                       .github/workflows/
  monorepo-targeted-deploy-with-secrets.yaml    deploy.yml
                                            services.json

ConcourseCore/k8s/                          ConcourseCore/k8s/
  (unchanged — same manifests)                (unchanged — same manifests)

administration/scripts/bash/                scripts/
  bake-secretmap.sh                           bake-secretmap.sh

administration/scripts/python/utilities/    scripts/
  get-secrets-from-yaml.py                    get-secrets-from-yaml.py
  requirements.txt                            requirements.txt

(ADO replacetokens@6 marketplace task)      scripts/
                                              replace-tokens.py

tech-enablement/config/                     (checked out at runtime from
  docker.k8.yml                              external repo — same as ADO)
```
finding:
In the Azure DevOps pipeline at monorepo-targeted-deploy-with-secrets.yaml:38-170:

Read monorepo-targeted-deploy-with-secrets.yaml, lines 38 to 90

Here it is! Lines 38-170 in the ADO pipeline show the service parameter with type: object containing all 19 services hardcoded as default: values.

Then later in the pipeline (around line 210+), ADO uses a loop to iterate through them:

Exactly! Line 235 shows: ${{ each service in parameters.service }}

This is Azure DevOps' special syntax that loops through the object array. GitHub Actions doesn't have this feature, so we:

Moved the service list from YAML → services.json
Changed ${{ each service }} loop → strategy: matrix with fromJson()
This gives the same result: one deployment job per service.

workflow should be at root with .github\workflows only