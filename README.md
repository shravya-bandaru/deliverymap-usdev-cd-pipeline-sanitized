# Deliverymap Service Pipeline Package (us-dev, Sanitized)

Pipeline deployment package for concourse-deliverymap-svc in us-dev environment.
All configuration values with 'id', 'secret', 'password', 'token', or 'key' in key names have been sanitized.


## Package Details

**Created:** 2026-02-03 09:20:33

## Sanitization

This package contains SANITIZED data. Configuration values with keys matching these patterns have been replaced with 'sanitized':

- Keys containing `id`
- Keys containing `secret`
- Keys containing `password`
- Keys containing `token`
- Keys containing `key`
- Keys containing `storage_account_name`
- Keys containing `_host`
- Keys containing `_url`
- Keys containing `_uri`
- Keys containing `_user`
- Keys containing `service_accounts`
- Keys containing `US_`
- Keys containing `pwcglb.com`
- Keys containing `pwcinternal.com`
- Keys containing `pwc.com`

### Example Sanitized Keys:
- `client_id` → `"sanitized"`
- `CLIENT_ID` → `"sanitized"`
- `tenant_id` → `"sanitized"`
- `buildId` → `"sanitized"`

## Contents

This package includes files from the following repositories:

### ConcourseCore/deploy/
- monorepo-targeted-deploy-with-secrets.yaml

### ConcourseCore/k8s/concourse-deliverymap-svc/
- deployment.yaml (sanitized)
- hpa.yaml (sanitized)

### ConcourseCore/k8s/concourse-deliverymap-svc/configs/us-dev/
- concourse-deliverymap-svc.configmap.yaml (sanitized)

### ConcourseCore/k8s/microservice-template/
- deployment.yaml (sanitized)
- service.yaml (sanitized)

### ConcourseCore/k8s/microservice-template/configs/us-dev/
- concourse-template-svc.configmap.yaml (sanitized)

### administration/scripts/bash/
- bake-secretmap.sh

### administration/scripts/python/utilities/
- get-secrets-from-yaml.py
- requirements.txt

### tech-enablement/config/
- docker.k8.yml (sanitized)

## Usage

Extract the package:
```bash
tar -xzf deliverymap-usdev-pipeline-sanitized.tar.gz
```

View contents:
```bash
tar -tzf deliverymap-usdev-pipeline-sanitized.tar.gz
```

## Source Specification

This package was generated from a YAML specification file that defines:
- Source file locations
- Destination paths in the tarball
- Which files to sanitize
- Sanitization patterns

To regenerate this package, use:
```bash
uv run --script create_pipeline_package.py --spec <spec-file.yaml>
```

## Additional Notes

This sanitized package is safe for analysis and sharing without exposing
sensitive identifiers. DO NOT use for actual deployments.

