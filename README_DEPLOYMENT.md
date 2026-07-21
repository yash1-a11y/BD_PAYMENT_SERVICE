# Deployment Guide

This documents how to build, run, and deploy the backend (FastAPI) and
frontend (Next.js) as production containers, and how to deploy both to
Kubernetes. It assumes an **externally-managed PostgreSQL instance** —
nothing here provisions, installs, or containerizes Postgres itself.

## 1. Building the images

```bash
# Backend
docker build -t bd-payment-backend:1.0.0 .

# Frontend — NEXT_PUBLIC_API_BASE_URL is baked into the JS bundle at BUILD
# time, not read at container runtime (a real Next.js constraint, not a
# bug). Every environment that needs a different backend URL needs its
# own image build with a different value here.
docker build -t bd-payment-frontend:1.0.0 \
  --build-arg NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.example \
  ./frontend
```

Always tag explicitly (`:1.0.0`, a date, or a commit SHA) — never
`:latest`, in either Docker or the Kubernetes manifests.

## 2. Running locally with Docker

Standalone, against an already-running Postgres (e.g. the existing
`docker/docker-compose.yml`, started separately — see below):

```bash
docker run --rm -p 8000:8000 \
  --env-file .env \
  -e DATABASE_URL="postgresql+psycopg://bd_payment:bd_payment@host.docker.internal:5432/bd_payment_service" \
  bd-payment-backend:1.0.0

docker run --rm -p 3000:3000 bd-payment-frontend:1.0.0
```

Or both together via the new root `docker-compose.yml` (backend +
frontend only — **no Postgres service**; point `DATABASE_URL` in your
`.env` at whatever Postgres you already have running, local or remote):

```bash
docker compose up -d --build
```

**Known limitation of this local compose setup**, confirmed by actually
running it: pages that fetch data server-side (the storefront listing/PDP
pages, rendered via Next.js Server Components) do so from *inside* the
frontend container, where `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`
resolves to the frontend container itself, not the backend container —
confirmed via the real error this produces:
```
TypeError: fetch failed ... ECONNREFUSED 127.0.0.1:8000
```
This compose file is for verifying both production images run and are
individually healthy — for full local development with working
server-side data fetches, keep using the existing non-Docker flow
(`uv run python main.py` + `cd frontend && npm run dev`, both on the host,
sharing the same real `localhost`), which every phase's docs already
document and which remains fully correct. In a real deployment (a single
public domain reachable by both the browser and any server-side fetch),
this limitation doesn't apply.

If you also want local Postgres, start it separately (unrelated,
untouched by this deployment work):
```bash
docker compose -f docker/docker-compose.yml up -d
```

## 3. Required environment variables

| Variable | Sensitive? | Who provides it | Default |
|---|---|---|---|
| `DATABASE_URL` | Yes | DevOps / DB team (external Postgres connection string) | none — required |
| `JWT_SECRET` | Yes | DevOps (long random value, unique per environment) | none — required |
| `TRANSFI_PUBLIC_KEY` | Yes | Transfi Merchant Dashboard | none — required |
| `TRANSFI_SECRET_KEY` | Yes | Transfi Merchant Dashboard | none — required |
| `TRANSFI_WEBHOOK_SECRET` | Yes | Transfi Merchant Dashboard (dedicated webhook secret, separate from the API secret key) | none — required |
| `TRANSFI_PAYMENT_LINK_ID` | No | Transfi Merchant Dashboard (Checkout Widget config) | none — required |
| `TRANSFI_BASE_URL` | No | Fixed | `https://checkout-server.transfi.com` |
| `TRANSFI_SUCCESS_URL` / `TRANSFI_FAILURE_URL` | No | Your domain | none — required |
| `JWT_EXPIRE_MINUTES` | No | — | `1440` |
| `PACKAGE_SYSTEM_BASE_URL` / `PACKAGE_SYSTEM_SRC` | No | — | already set |
| `ALLOWED_ORIGINS` | No | Your domain(s), JSON array | none — required |
| `APP_ENV` | No | — | `production` |
| `LOG_LEVEL` | No | — | `INFO` |
| `NEXT_PUBLIC_API_BASE_URL` | No | DevOps — **build-time only**, see §1 | none — required at build |

The app (`src/config/settings.py`) refuses to start if any required
(no-default) variable is missing — this is intentional, matching this
project's existing secrets-hardening rule from earlier in its history.

The five genuinely sensitive values (`DATABASE_URL`, `JWT_SECRET`, the two
Transfi keys, and the webhook secret) must come from a Kubernetes
`Secret`, never a `ConfigMap`, never a hardcoded value anywhere.

## 4. Kubernetes deployment

Files live in `k8s/`. Apply order:

```bash
# 1. Non-sensitive config — fill in the blank per-environment values in
#    k8s/backend-configmap.yaml first (TRANSFI_BASE_URL,
#    TRANSFI_PAYMENT_LINK_ID, TRANSFI_SUCCESS_URL, TRANSFI_FAILURE_URL,
#    ALLOWED_ORIGINS — see the table above for the real value each one
#    needs). An unfilled ALLOWED_ORIGINS makes the app refuse to start,
#    by design; the other blank fields start the app but break
#    checkout/webhooks at runtime.
kubectl apply -f k8s/backend-configmap.yaml

# k8s/frontend-configmap.yaml is NOT applied here and is not referenced
# by frontend-deployment.yaml — it exists only for documentation/
# structural consistency. NEXT_PUBLIC_API_BASE_URL is inlined into the
# frontend's JS bundle at Docker BUILD time (`--build-arg`, see §1) —
# applying or editing this ConfigMap has zero effect on a running
# frontend pod. To change it, rebuild and roll out a new frontend image.

# 2. Real secrets — created directly, NOT by applying secret.example.yaml
#    (that file is a template with empty placeholders, deliberately named
#    .example so it's never mistaken for something deployable)
kubectl create secret generic bd-payment-secrets \
  --from-literal=DATABASE_URL='postgresql+psycopg://<user>:<password>@<host>:5432/<database>' \
  --from-literal=JWT_SECRET='<long random value>' \
  --from-literal=TRANSFI_PUBLIC_KEY='<from Transfi dashboard>' \
  --from-literal=TRANSFI_SECRET_KEY='<from Transfi dashboard>' \
  --from-literal=TRANSFI_WEBHOOK_SECRET='<from Transfi dashboard>'

# 3. Deployments + Services
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
```

Both Deployments run 2 replicas, `RollingUpdate` with `maxUnavailable: 0`
(no downtime during a rollout), explicit resource requests/limits, and
readiness + liveness probes (`/health` for the backend — reuses the
existing endpoint that already checks real DB connectivity;
`/api/health` for the frontend, added specifically for this).

### Running migrations

Matching this project's own established convention (every phase's docs
run `alembic upgrade head` as a distinct manual step, never automatically
on app start): the backend Deployment sets `RUN_MIGRATIONS_ON_STARTUP=false`
explicitly. To actually run migrations against a real environment:

```bash
kubectl run bd-payment-migrate --rm -it --restart=Never \
  --image=bd-payment-backend:1.0.0 \
  --env-from=configmap/bd-payment-backend-config \
  --env-from=secret/bd-payment-secrets \
  --command -- alembic upgrade head
```

(Or set `RUN_MIGRATIONS_ON_STARTUP=true` as an env override on a single
one-off pod — never on the running Deployment itself, to avoid every
replica racing to run migrations concurrently on every restart.)

### Rollback

```bash
kubectl rollout history deployment/bd-payment-backend
kubectl rollout undo deployment/bd-payment-backend            # previous revision
kubectl rollout undo deployment/bd-payment-backend --to-revision=<N>
```

Same commands apply to `bd-payment-frontend`. Because `maxUnavailable: 0`
is set, both rollouts and rollbacks happen without a period of zero
healthy pods.

## 5. Connecting to external PostgreSQL

The app never provisions, installs, or runs Postgres itself — it only
ever reads `DATABASE_URL` (via `src/config/settings.py` →
`src/db/base.py`) and connects to whatever real Postgres instance that
string points at. Nothing in any Dockerfile or Kubernetes manifest in this
repo creates a database container; `DATABASE_URL`'s value is entirely a
deployment-time concern, supplied via the `Secret` above.

## 6. Assumptions made

- Base images: `python:3.14-slim` (backend, matching this project's actual
  `requires-python = ">=3.14"`) and `node:22-slim` (frontend — an LTS
  release; the exact Node version wasn't pinned anywhere in the existing
  project).
- `RUN_MIGRATIONS_ON_STARTUP` is a new convention introduced by this
  deployment work specifically to keep migrations manual by default,
  matching how every phase's own docs already run them — not something
  that existed in the app before.
- Resource requests/limits (`100m`/`500m` CPU, `256Mi`/`512Mi` memory) are
  reasonable starting points for this app's actual size, not measured
  against real production load — tune based on real usage.
- No live Kubernetes cluster was available in this environment to fully
  validate the manifests server-side; they were validated for structural
  YAML correctness and standard Kubernetes API shape, but not applied
  against a real API server. Recommend a `--dry-run=server` pass (or
  applying to a staging cluster) before first real production use.

## 7. Confirmation: no secrets are exposed anywhere in this repository

Verified directly (not assumed) as part of this work:
- Every Dockerfile, `docker-compose.yml`, and every file under `k8s/`
  contains environment variable **names** only — zero literal secret
  values anywhere in any of them.
- `k8s/secret.example.yaml` ships with empty string values and is named
  `.example` specifically so it can never be mistaken for a real,
  deployable Secret.
- `.env.example` contains placeholder text only (`replace-with-...` /
  blank), matching the pattern already established earlier in this
  project for the existing Transfi credentials.
- The real `.env` (which does hold live credentials for local dev) is,
  and has always been, `.gitignore`'d — confirmed via `git log --all` and
  a full-history search that it has never been committed, on any branch.
- A full `git log --all -p` search for every real secret value used in
  this project (Transfi public/secret keys, webhook secret) returned zero
  matches anywhere in git history.
