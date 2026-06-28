# ziy.one on Kubernetes

Deploys the Astro site to the `moko-bored-snake` cluster behind ingress-nginx,
with TLS auto-issued **and auto-renewed** by cert-manager. This replaces the old
standalone DigitalOcean host (`64.23.157.26`), whose Let's Encrypt cert stopped
renewing because the site was never actually migrated onto the cluster.

## What's here

| File                         | Purpose                                            |
| ---------------------------- | -------------------------------------------------- |
| `base/deployment.yaml`       | nginx serving static `dist/`, hardened, 2 replicas |
| `base/service.yaml`          | ClusterIP `:80 -> :8080`                            |
| `base/ingress.yaml`          | `ziy.one` + TLS (`ziyone-tls`)                      |
| `base/ingress-www-redirect.yaml` | `www.ziy.one` -> 301 `https://ziy.one`         |
| `overlays/prod/`             | namespace `ziy` + image tag (CI-bumped)            |
| `argocd-application.yaml`    | ArgoCD `ziyone-prod` app                            |

Image is built by `.github/workflows/deploy-k8s.yml` to
`ghcr.io/akz142857/ziyone-web` and the overlay tag is bumped per push.

## TLS: DNS-01 via Cloudflare

The `ziy.one` Ingress uses `cert-manager.io/cluster-issuer: letsencrypt-cloudflare`
(DNS-01). For issuance to succeed, three prerequisites must be true:

1. **`ziy.one` zone lives in the same Cloudflare account** as the existing zones
   (`boredsnakes.com`, `somain.ai`, `claycosmos.ai`, `install9.ai`) — move it
   off GoDaddy: add the zone in Cloudflare, update the registrar nameservers.
2. **The Cloudflare API token** (`cloudflare-api-token` secret in `cert-manager`)
   must have `Zone:DNS:Edit` on `ziy.one`. If it's account-scoped (all zones),
   adding the zone is enough; if zone-scoped, regenerate it to include `ziy.one`.
3. **The ClusterIssuer must list `ziy.one`** in its solver `dnsZones`. This issuer
   is live-managed (not in claycosmos-infra), so patch it directly:

   ```bash
   kubectl patch clusterissuer letsencrypt-cloudflare --type=json -p='[
     {"op":"add","path":"/spec/acme/solvers/0/selector/dnsZones/-","value":"ziy.one"}
   ]'
   ```

> Fallback: to use HTTP-01 instead (no Cloudflare needed, just an A record at the
> ingress), change both Ingress annotations to `letsencrypt-prod`. This is what
> `nodalos` uses.

## One-time bring-up (ordered)

```bash
export KUBECONFIG=/Users/ziy/.kube/config

# 1. Move ziy.one DNS to Cloudflare; satisfy the 3 TLS prereqs above.

# 2. Point traffic at the cluster ingress (in Cloudflare DNS):
#      A  ziy.one      -> 104.130.53.105   (DNS-only / grey cloud while issuing)
#      A  www.ziy.one  -> 104.130.53.105

# 3. Namespace + GHCR pull secret (package is private):
kubectl create namespace ziy
kubectl get secret ghcr-credentials -n nodalos -o yaml \
  | grep -v '^\s*\(namespace\|resourceVersion\|uid\|creationTimestamp\):' \
  | kubectl apply -n ziy -f -

# 4. First image build: trigger the workflow (push to main or run it manually),
#    confirm ghcr.io/akz142857/ziyone-web:sha-XXXX exists and the overlay tag bumped.

# 5. Register with ArgoCD:
kubectl apply -f infra/k8s/argocd-application.yaml

# 6. Watch issuance + rollout:
kubectl -n ziy get certificate,pod,ingress
kubectl -n ziy describe certificate ziyone-tls   # Ready=True when issued
```

After `ziyone-tls` is Ready, you can switch Cloudflare to proxied (orange) if
desired. Renewal is automatic ~30 days before expiry — no further action.

## Notes

- Container base images come from the ECR Docker mirror, not Docker Hub, to dodge
  the cluster's shared-egress anonymous pull-rate limit (see claycosmos-infra).
- GitHub Pages (`/ZiyOne`) deploy is unchanged and still works in parallel; the
  apex build flips `ASTRO_BASE=/` via Docker build args.
