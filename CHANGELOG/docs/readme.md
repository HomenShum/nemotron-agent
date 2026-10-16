# README history

Surface: [README.md](../../README.md)

## 2026-10-15 — source-backed developer handoff

- User problem: a developer could see deployment instructions without a local entrypoint or a clear distinction between service health and working model access.
- Change: add a source-backed setup preface, entrypoint map, caller-supplied history and streaming limits; retain the original overview and deployment text.
- Evidence checked: [application](https://github.com/HomenShum/nemotron-agent/blob/641a52c5414700fc9a8c351045dbe716f5adbc09/app/main.py), [dependency pins](https://github.com/HomenShum/nemotron-agent/blob/641a52c5414700fc9a8c351045dbe716f5adbc09/requirements.txt), [container declaration](https://github.com/HomenShum/nemotron-agent/blob/641a52c5414700fc9a8c351045dbe716f5adbc09/Dockerfile) and [workflow declaration](https://github.com/HomenShum/nemotron-agent/blob/641a52c5414700fc9a8c351045dbe716f5adbc09/.github/workflows/docker-publish.yml), pinned to commit `641a52c5414700fc9a8c351045dbe716f5adbc09`.
- Checks not run / remaining limits: this source-only review did not perform an install, application import/run, container build, provider/model call, workflow-run check or deployment verification. The system-role difference is observed in source only. No current throughput, model-quality or production-readiness claim is made.
