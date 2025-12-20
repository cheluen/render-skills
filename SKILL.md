---
name: render-api
description: Manage Render cloud resources via API. Deploy services, databases (Postgres/Redis), domains, logs. Works with Free Plan. Use for Render deployments and infrastructure automation.
---

# Render API Skill

Manage Render cloud platform: services, databases, domains, logs, blueprints.

## Free Plan Support

**API works with Free Plan.** Limitations:
- Services auto-sleep after 15 min inactivity
- Postgres expires after 30 days
- Key Value data ephemeral (lost on restart)
- Max 2 custom domains, 1 project
- No horizontal autoscaling

## Configuration

**config.json** (in skill directory):
```json
{
  "mode": "json",
  "default_profile": "default",
  "profiles": {
    "default": { "api_key": "rnd_xxx" },
    "company": { "api_key": "rnd_yyy" }
  }
}
```

Or use `"mode": "env"` to read from environment:
```bash
export RENDER_API_KEY="rnd_xxx"
# Multiple: export RENDER_API_KEYS="rnd_xxx,rnd_yyy"
```

Get API key: https://dashboard.render.com/u/settings#api-keys

## Quick Reference

### Services
```bash
# List
curl -s "https://api.render.com/v1/services" -H "Authorization: Bearer $RENDER_API_KEY"

# Deploy
curl -X POST "https://api.render.com/v1/services/{id}/deploys" \
  -H "Authorization: Bearer $RENDER_API_KEY" -H "Content-Type: application/json" \
  -d '{"clearCache":"do_not_clear"}'

# Suspend/Resume/Restart
curl -X POST "https://api.render.com/v1/services/{id}/suspend" -H "Authorization: Bearer $RENDER_API_KEY"
curl -X POST "https://api.render.com/v1/services/{id}/resume" -H "Authorization: Bearer $RENDER_API_KEY"
curl -X POST "https://api.render.com/v1/services/{id}/restart" -H "Authorization: Bearer $RENDER_API_KEY"
```

### Databases
```bash
# Postgres
curl -s "https://api.render.com/v1/postgres" -H "Authorization: Bearer $RENDER_API_KEY"
curl -s "https://api.render.com/v1/postgres/{id}/connection-info" -H "Authorization: Bearer $RENDER_API_KEY"

# Key Value (Redis)
curl -s "https://api.render.com/v1/key-value" -H "Authorization: Bearer $RENDER_API_KEY"
curl -s "https://api.render.com/v1/key-value/{id}/connection-info" -H "Authorization: Bearer $RENDER_API_KEY"
```

### Other Operations
```bash
# Logs
curl -s "https://api.render.com/v1/logs?resource={serviceId}&limit=100" -H "Authorization: Bearer $RENDER_API_KEY"

# Env vars
curl -s "https://api.render.com/v1/services/{id}/env-vars" -H "Authorization: Bearer $RENDER_API_KEY"

# Custom domains
curl -s "https://api.render.com/v1/services/{id}/custom-domains" -H "Authorization: Bearer $RENDER_API_KEY"

# Blueprints
curl -X POST "https://api.render.com/v1/blueprints/{id}/sync" -H "Authorization: Bearer $RENDER_API_KEY"

# One-off job
curl -X POST "https://api.render.com/v1/services/{id}/jobs" \
  -H "Authorization: Bearer $RENDER_API_KEY" -H "Content-Type: application/json" \
  -d '{"startCommand":"npm run migrate"}'
```

## CLI Scripts

```bash
# Bash (zero deps)
./scripts/render-api.sh services list
./scripts/render-api.sh deploys trigger srv-xxx
./scripts/render-api.sh batch services  # all profiles

# Python (stdlib only)
python scripts/render_client.py services
python scripts/render_client.py batch services
```

## Rate Limits

| Operation | Limit |
|-----------|-------|
| GET | 400/min |
| POST/PATCH/DELETE | 30/min |
| Deploy/Suspend | 10/min/service |
| Create service | 20/hour |

## Error Codes

- `401`: Check API key (Free plan keys work fine)
- `403`: May need paid plan (autoscaling, previews)
- `429`: Rate limited, retry with backoff

## References

- [API-REFERENCE.md](API-REFERENCE.md) - Full endpoint docs
- [EXAMPLES.md](EXAMPLES.md) - Workflow examples
- https://api-docs.render.com
