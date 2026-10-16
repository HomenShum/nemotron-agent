# Docker packaging workflow history

Surface: [Docker workflow](../../.github/workflows/docker-publish.yml) · [History index](../README.md)

## 2026-10-15 — Restore the existing workflow after inactivity

A developer reviewing the handoff PR could see historical successful builds while no fresh packaging job appeared. The repository workflow was observed as `disabled_inactivity`; its enabled setting was restored and read back as `active`. The workflow file and application behavior were unchanged.

Before: `disabled_inactivity`. After: `active`. This records the observed repository setting, not a passing build result. Inspect the native build result for the exact revision being reviewed. GitHub documents [workflow re-enablement](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows).

The existing workflow builds the container for pull requests without registry publication/signing. Main and scheduled events can publish to GHCR and sign the image. Packaging does not test endpoints, authentication or model access.

Scope and limits: restore the existing enabled setting and record this history. No workflow YAML, dependency, app, model, provider, branch-protection or service-deployment change. No application/provider call or runtime-readiness result was produced by the settings repair.
