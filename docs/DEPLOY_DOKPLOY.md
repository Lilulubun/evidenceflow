# Dokploy Application deployment

Deploy KerjaKita AI as one Dokploy **Application** using its root Dockerfile. No Compose deployment is required or supported by this guide.

## Create application

1. Dokploy → **Create Application** → GitHub provider.
2. Repository: `Lilulubun/kerjakita-ai`; branch: `main`.
3. Build Type: **Dockerfile**.
4. Dockerfile Path: `./Dockerfile`.
5. Docker Context Path: `.`.
6. Save. Configure volume, runtime environment and access gate below before first deployment/public routing. Then click **Deploy**.

Dokploy Dockerfile build fields and paths follow the official [Build Type documentation](https://docs.dokploy.com/docs/core/applications/build-type). Dockerfile uses `python:3.14-slim`, stdlib only, and runs as UID/GID `10001` (`app`).

## Application settings

- **Replicas:** `1`. JSON store is single-process; do not scale horizontally. Set update and rollback order to `stop-first` so old and new processes never write the same volume concurrently. Pin service to the volume's node on multi-node installations; local named volumes do not migrate. Keep demo writes serialized; this JSON store has no concurrent-write transaction safety.
- **Internal/container port:** `8000` (HTTP).
- **Published host port:** none. Create routing through Dokploy **Domains** only; domain container port is internal routing, not direct host exposure.
- **Volume:** create one named Docker volume, mount `/data`.
- **Environment:**

```text
EVIDENCEFLOW_HOST=0.0.0.0
EVIDENCEFLOW_PORT=8000
EVIDENCEFLOW_STATE_FILE=/data/runtime_state.json
EVIDENCEFLOW_AI_SETTINGS_FILE=/data/runtime_ai_settings.json
```

Keep AI disabled until access restriction is active. Configure API keys only in Dokploy runtime Environment Variables or KerjaKita AI settings UI after gate verification; never commit secrets or pass keys as build arguments. Optional runtime names: `EVIDENCEFLOW_AI_ENABLED`, `EVIDENCEFLOW_AI_API_KEY`, `EVIDENCEFLOW_AI_BASE_URL`, `EVIDENCEFLOW_AI_CHAT_MODEL`, `EVIDENCEFLOW_AI_TEMPERATURE`, `EVIDENCEFLOW_AI_TOKEN_LIMIT`, `EVIDENCEFLOW_AI_PROVIDER`. Stored settings override environment defaults. Saved key remains plaintext server-side in `/data/runtime_ai_settings.json` (mode `0600`); secure volume backups too. `GET /api/settings` masks saved key. Health `mode` derives from environment, while `aiState.state` reflects last provider call: configuring credentials alone does not prove live AI.

## HTTPS and access gate

1. Add Domain in Dokploy **Domains** tab, route container port `8000`, enable **HTTPS**, select Let’s Encrypt/certificate. Follow official [Domains documentation](https://docs.dokploy.com/docs/core/domains).
2. Enable Dokploy application **Security → Basic Authentication** (or an equivalent external access restriction at your identity gateway) before public access. Use a strong password entered into Dokploy’s masked UI; do not put credentials in this repository.
3. Verify unauthenticated requests are rejected before enabling AI. Demo actor selector is not authentication; settings endpoint is not authentication.

Dokploy manages Application domain routing through Traefik configuration and supports hot reload without redeploy. Domain HTTPS and access settings require live Dokploy verification; this repository does not claim them configured.

## Persistence and first mount

`/data` stores `runtime_state.json` and `runtime_ai_settings.json`. Do **not** use a host bind mount. Never run `docker compose down -v` (this deployment is not Compose); do not delete the named volume when removing/redeploying an Application.

Docker named-volume first-mount ownership must be verified on target Dokploy host. Image creates `/data` as UID/GID `10001:10001` before `USER 10001:10001`, but Docker may initialize an empty named volume according to engine behavior. After first deployment, verify:

```sh
docker inspect <container> --format '{{json .Mounts}}'
docker exec <container> sh -c 'id; stat -c "%u:%g %a %n" /data'
docker exec <container> sh -c 'test -w /data && echo DATA_WRITABLE'
```

If ownership is not `10001:10001` and writes fail, fix volume ownership through Dokploy’s supported run-command/volume workflow, then redeploy and repeat checks. Do not weaken container to root.

## Verification checklist

- `GET https://<domain>/health` returns JSON `status: ok`.
- `/`, `/graph`, `/tkt3`, `/api/tkt3` load.
- `/api/graph` research source shows fixture graph; runtime source starts empty.
- Save synthetic setting in UI; restart/redeploy; verify setting remains masked and state remains.
- Keep one replica.
- Validate access gate before entering AI keys.

Native smoke command (Docker unavailable locally):

```sh
python3 docs/smoke_deploy.py
```

This uses isolated temporary state, checks same host/port/env paths, static assets, graph sources, TKT3 fixture, settings mode/permissions, synthetic capture, and persistence across process restart. It does not prove Docker build, named-volume initialization, Dokploy routing, HTTPS, or access restriction.

## Verification record (2026-10-17)

Python `3.14.7`, isolated scratch copies; original runtime JSON hashes unchanged:

```text
python3 docs/smoke_deploy.py
PASS health/workspace/static/graph/settings/tkt3; runtime empty, research fixture present
PASS confirmed synthetic evidence + AI settings survive process restart; settings mode 0600
DEPLOY_SMOKE_OK native Python; container build/UID/volume/proxy still require Docker host

python3 run_checks.py       # all local checks passed
python3 demo_scenario.py    # DEMO_OK full scenario reproduced over HTTP
python3 test_ui.py          # UI_SMOKE_OK (HTTP/API checks, not browser automation)
python3 test_ai_adapter.py  # ai adapter checks passed
```

`docker build -t evidenceflow:deployment-check .` was attempted and blocked:

```text
Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
```

No `podman`, `nerdctl`, or `rootlesskit` available. No daemon started or permission bypass attempted. Container build, UID, volume initialization, live AI, HTTPS and gateway remain unverified. No deployment performed. `GET /health` only checks process liveness; test capture/settings writes to establish storage readiness.

Rollback: redeploy prior `main` commit in Dokploy; preserve `/data` volume unless data loss is explicitly intended.
