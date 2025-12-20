# Render API Reference

Complete API endpoint reference for the Render cloud platform.

## Table of Contents

1. [Services](#services)
2. [Deploys](#deploys)
3. [Environment Variables](#environment-variables)
4. [Custom Domains](#custom-domains)
5. [Postgres](#postgres)
6. [Key Value](#key-value)
7. [Jobs](#jobs)
8. [Blueprints](#blueprints)
9. [Logs](#logs)
10. [Disks](#disks)
11. [Workspaces](#workspaces)

---

## Services

### List Services

```
GET /v1/services
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| name | string | Filter by service name (partial match) |
| type | string | Filter by type: `web_service`, `static_site`, `background_worker`, `private_service`, `cron_job` |
| env | string | Filter by environment: `docker`, `elixir`, `go`, `node`, `python`, `ruby`, `rust`, `image` |
| region | string | Filter by region: `oregon`, `frankfurt`, `ohio`, `singapore`, `virginia` |
| suspended | string | Filter by suspended state: `suspended`, `not_suspended` |
| createdBefore | datetime | Filter services created before date (ISO 8601) |
| createdAfter | datetime | Filter services created after date (ISO 8601) |
| updatedBefore | datetime | Filter services updated before date |
| updatedAfter | datetime | Filter services updated after date |
| ownerId | string | Filter by owner (workspace) ID |
| cursor | string | Pagination cursor |
| limit | integer | Results per page (default: 20, max: 100) |

**Response:**
```json
[
  {
    "service": {
      "id": "srv-xxxxx",
      "name": "my-service",
      "ownerId": "tea-xxxxx",
      "type": "web_service",
      "repo": "https://github.com/user/repo",
      "autoDeploy": "yes",
      "branch": "main",
      "suspended": "not_suspended",
      "suspenders": [],
      "serviceDetails": {
        "env": "node",
        "region": "oregon",
        "plan": "starter",
        "numInstances": 1,
        "buildCommand": "npm install",
        "startCommand": "npm start",
        "url": "https://my-service.onrender.com"
      },
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z"
    },
    "cursor": "abc123"
  }
]
```

### Create Service

```
POST /v1/services
```

**Request Body (Web Service):**
```json
{
  "type": "web_service",
  "name": "my-app",
  "ownerId": "tea-xxxxx",
  "repo": "https://github.com/user/repo",
  "autoDeploy": "yes",
  "branch": "main",
  "serviceDetails": {
    "env": "node",
    "region": "oregon",
    "plan": "starter",
    "buildCommand": "npm install",
    "startCommand": "npm start",
    "envVars": [
      {"key": "NODE_ENV", "value": "production"}
    ]
  }
}
```

**Request Body (Static Site):**
```json
{
  "type": "static_site",
  "name": "my-site",
  "ownerId": "tea-xxxxx",
  "repo": "https://github.com/user/repo",
  "autoDeploy": "yes",
  "branch": "main",
  "serviceDetails": {
    "buildCommand": "npm run build",
    "publishPath": "dist"
  }
}
```

### Retrieve Service

```
GET /v1/services/{serviceId}
```

### Update Service

```
PATCH /v1/services/{serviceId}
```

**Request Body:**
```json
{
  "name": "updated-name",
  "autoDeploy": "no",
  "branch": "develop",
  "serviceDetails": {
    "plan": "standard",
    "numInstances": 2
  }
}
```

### Delete Service

```
DELETE /v1/services/{serviceId}
```

### Suspend Service

```
POST /v1/services/{serviceId}/suspend
```

### Resume Service

```
POST /v1/services/{serviceId}/resume
```

### Restart Service

```
POST /v1/services/{serviceId}/restart
```

### Scale Service

```
POST /v1/services/{serviceId}/scale
```

**Request Body:**
```json
{
  "numInstances": 3
}
```

### Update Autoscaling

```
PUT /v1/services/{serviceId}/autoscaling
```

**Request Body:**
```json
{
  "enabled": true,
  "min": 1,
  "max": 10,
  "criteria": {
    "cpu": {"enabled": true, "percentage": 70},
    "memory": {"enabled": true, "percentage": 80}
  }
}
```

### List Instances

```
GET /v1/services/{serviceId}/instances
```

### Purge Cache (Web Services)

```
POST /v1/services/{serviceId}/cache/purge
```

---

## Deploys

### List Deploys

```
GET /v1/services/{serviceId}/deploys
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| startTime | datetime | Filter by deploy start time |
| endTime | datetime | Filter by deploy end time |
| cursor | string | Pagination cursor |
| limit | integer | Results per page |

**Response:**
```json
[
  {
    "deploy": {
      "id": "dep-xxxxx",
      "commit": {
        "id": "abc123",
        "message": "Update code",
        "createdAt": "2024-01-01T00:00:00Z"
      },
      "status": "live",
      "trigger": "api",
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z",
      "finishedAt": "2024-01-01T00:05:00Z"
    }
  }
]
```

**Deploy Status Values:**
- `created`: Deploy initiated
- `build_in_progress`: Building
- `update_in_progress`: Updating
- `live`: Successfully deployed
- `deactivated`: Replaced by newer deploy
- `build_failed`: Build failed
- `update_failed`: Update failed
- `canceled`: Manually canceled

### Trigger Deploy

```
POST /v1/services/{serviceId}/deploys
```

**Request Body:**
```json
{
  "clearCache": "do_not_clear"
}
```

**clearCache Options:**
- `do_not_clear`: Keep build cache (default)
- `clear`: Clear build cache

### Retrieve Deploy

```
GET /v1/services/{serviceId}/deploys/{deployId}
```

### Cancel Deploy

```
POST /v1/services/{serviceId}/deploys/{deployId}/cancel
```

### Rollback

```
POST /v1/services/{serviceId}/rollback
```

**Request Body:**
```json
{
  "deployId": "dep-xxxxx"
}
```

---

## Environment Variables

### List Environment Variables

```
GET /v1/services/{serviceId}/env-vars
```

**Response:**
```json
[
  {
    "envVar": {
      "key": "NODE_ENV",
      "value": "production"
    }
  },
  {
    "envVar": {
      "key": "DATABASE_URL",
      "value": null,
      "generateValue": true
    }
  }
]
```

### Update Environment Variables

```
PUT /v1/services/{serviceId}/env-vars
```

**Request Body:**
```json
[
  {"key": "NODE_ENV", "value": "production"},
  {"key": "API_KEY", "generateValue": true}
]
```

### Get Single Environment Variable

```
GET /v1/services/{serviceId}/env-vars/{envVarKey}
```

### Update Single Environment Variable

```
PUT /v1/services/{serviceId}/env-vars/{envVarKey}
```

**Request Body:**
```json
{
  "value": "new-value"
}
```

### Delete Environment Variable

```
DELETE /v1/services/{serviceId}/env-vars/{envVarKey}
```

---

## Custom Domains

### List Custom Domains

```
GET /v1/services/{serviceId}/custom-domains
```

**Response:**
```json
[
  {
    "customDomain": {
      "id": "cdm-xxxxx",
      "name": "example.com",
      "domainType": "apex",
      "publicSuffix": "com",
      "redirectForName": null,
      "verificationStatus": "verified",
      "createdAt": "2024-01-01T00:00:00Z"
    }
  }
]
```

### Add Custom Domain

```
POST /v1/services/{serviceId}/custom-domains
```

**Request Body:**
```json
{
  "name": "example.com"
}
```

### Retrieve Custom Domain

```
GET /v1/services/{serviceId}/custom-domains/{customDomainIdOrName}
```

### Delete Custom Domain

```
DELETE /v1/services/{serviceId}/custom-domains/{customDomainIdOrName}
```

### Verify DNS

```
POST /v1/services/{serviceId}/custom-domains/{customDomainIdOrName}/verify
```

---

## Postgres

### List Postgres Instances

```
GET /v1/postgres
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| name | string | Filter by name |
| region | string | Filter by region |
| suspended | string | Filter by state |
| ownerId | string | Filter by owner |
| cursor | string | Pagination cursor |
| limit | integer | Results per page |

### Create Postgres

```
POST /v1/postgres
```

**Request Body:**
```json
{
  "name": "my-database",
  "ownerId": "tea-xxxxx",
  "region": "oregon",
  "plan": "starter",
  "version": "15",
  "databaseName": "mydb",
  "databaseUser": "admin",
  "highAvailabilityEnabled": false
}
```

**Plan Options:**
- `free`: Free tier (limited)
- `starter`: 256MB RAM
- `standard`: 1GB RAM
- `pro`: 4GB+ RAM

### Retrieve Postgres

```
GET /v1/postgres/{postgresId}
```

### Update Postgres

```
PATCH /v1/postgres/{postgresId}
```

### Delete Postgres

```
DELETE /v1/postgres/{postgresId}
```

### Get Connection Info

```
GET /v1/postgres/{postgresId}/connection-info
```

**Response:**
```json
{
  "internalConnectionString": "postgresql://...",
  "externalConnectionString": "postgresql://...",
  "psqlCommand": "PGPASSWORD=xxx psql -h xxx -p 5432 -U xxx",
  "host": "xxx.oregon-postgres.render.com",
  "port": 5432,
  "database": "mydb",
  "user": "admin",
  "password": "xxx"
}
```

### Suspend Postgres

```
POST /v1/postgres/{postgresId}/suspend
```

### Resume Postgres

```
POST /v1/postgres/{postgresId}/resume
```

### Restart Postgres

```
POST /v1/postgres/{postgresId}/restart
```

### Trigger Failover (HA)

```
POST /v1/postgres/{postgresId}/failover
```

---

## Key Value

### List Key Value Instances

```
GET /v1/key-value
```

### Create Key Value

```
POST /v1/key-value
```

**Request Body:**
```json
{
  "name": "my-cache",
  "ownerId": "tea-xxxxx",
  "region": "oregon",
  "plan": "starter",
  "maxmemoryPolicy": "allkeys-lru"
}
```

**maxmemoryPolicy Options:**
- `noeviction`: Return error when memory limit reached
- `allkeys-lru`: Evict least recently used keys
- `allkeys-lfu`: Evict least frequently used keys
- `allkeys-random`: Evict random keys
- `volatile-lru`: Evict LRU keys with TTL set
- `volatile-lfu`: Evict LFU keys with TTL set
- `volatile-random`: Evict random keys with TTL set
- `volatile-ttl`: Evict keys with shortest TTL

### Retrieve Key Value

```
GET /v1/key-value/{keyValueId}
```

### Update Key Value

```
PATCH /v1/key-value/{keyValueId}
```

### Delete Key Value

```
DELETE /v1/key-value/{keyValueId}
```

### Get Connection Info

```
GET /v1/key-value/{keyValueId}/connection-info
```

**Response:**
```json
{
  "internalConnectionString": "redis://...",
  "externalConnectionString": "rediss://...",
  "redisCLICommand": "redis-cli -u rediss://..."
}
```

### Suspend Key Value

```
POST /v1/key-value/{keyValueId}/suspend
```

### Resume Key Value

```
POST /v1/key-value/{keyValueId}/resume
```

---

## Jobs

### List Jobs

```
GET /v1/services/{serviceId}/jobs
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | Filter by status: `pending`, `running`, `succeeded`, `failed`, `canceled` |
| createdBefore | datetime | Filter by creation date |
| createdAfter | datetime | Filter by creation date |
| startedBefore | datetime | Filter by start date |
| startedAfter | datetime | Filter by start date |
| finishedBefore | datetime | Filter by finish date |
| finishedAfter | datetime | Filter by finish date |
| cursor | string | Pagination cursor |
| limit | integer | Results per page |

### Create Job

```
POST /v1/services/{serviceId}/jobs
```

**Request Body:**
```json
{
  "startCommand": "npm run db:migrate",
  "planOverride": "standard"
}
```

### Retrieve Job

```
GET /v1/services/{serviceId}/jobs/{jobId}
```

### Cancel Job

```
POST /v1/services/{serviceId}/jobs/{jobId}/cancel
```

---

## Blueprints

### List Blueprints

```
GET /v1/blueprints
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| ownerId | string[] | Filter by owner IDs |
| cursor | string | Pagination cursor |
| limit | integer | Results per page |

### Retrieve Blueprint

```
GET /v1/blueprints/{blueprintId}
```

### Update Blueprint

```
PATCH /v1/blueprints/{blueprintId}
```

**Request Body:**
```json
{
  "name": "Updated Name",
  "branch": "main",
  "autoDeploy": true
}
```

### Sync Blueprint

```
POST /v1/blueprints/{blueprintId}/sync
```

### Disconnect Blueprint

```
POST /v1/blueprints/{blueprintId}/disconnect
```

### List Blueprint Syncs

```
GET /v1/blueprints/{blueprintId}/syncs
```

---

## Logs

### List Logs

```
GET /v1/logs
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| resource | string[] | **Required.** Resource IDs to query |
| startTime | datetime | Start of time range (ISO 8601) |
| endTime | datetime | End of time range |
| text | string[] | Filter by log text |
| level | string[] | Filter by level: `info`, `warn`, `error` |
| type | string[] | Filter by type: `app`, `request`, `build` |
| host | string[] | Filter request logs by host |
| statusCode | string[] | Filter request logs by status code |
| method | string[] | Filter request logs by HTTP method |
| path | string[] | Filter request logs by path |
| instance | string[] | Filter by instance ID |
| limit | integer | Max results |
| direction | string | `forward` or `backward` (default) |

**Response:**
```json
{
  "logs": [
    {
      "id": "log-xxxxx",
      "resourceId": "srv-xxxxx",
      "timestamp": "2024-01-01T00:00:00.000Z",
      "level": "info",
      "type": "app",
      "message": "Server started on port 3000"
    }
  ],
  "hasMore": true,
  "nextStartTime": "2024-01-01T00:00:01.000Z",
  "nextEndTime": "2024-01-01T00:01:00.000Z"
}
```

### Subscribe to Logs (Streaming)

```
GET /v1/logs/subscribe
```

Uses Server-Sent Events (SSE) for real-time log streaming.

### List Log Label Values

```
GET /v1/logs/labels/{label}/values
```

**Labels:** `level`, `type`, `host`, `statusCode`, `method`, `instance`

---

## Disks

### List Disks

```
GET /v1/disks
```

### Create Disk

```
POST /v1/disks
```

**Request Body:**
```json
{
  "name": "my-disk",
  "serviceId": "srv-xxxxx",
  "sizeGB": 10,
  "mountPath": "/data"
}
```

### Retrieve Disk

```
GET /v1/disks/{diskId}
```

### Update Disk

```
PATCH /v1/disks/{diskId}
```

**Request Body:**
```json
{
  "name": "updated-name",
  "sizeGB": 20
}
```

### Delete Disk

```
DELETE /v1/disks/{diskId}
```

### List Snapshots

```
GET /v1/disks/{diskId}/snapshots
```

### Create Snapshot

```
POST /v1/disks/{diskId}/snapshots
```

---

## Workspaces

### List Workspaces

```
GET /v1/owners
```

**Response:**
```json
[
  {
    "owner": {
      "id": "tea-xxxxx",
      "name": "My Team",
      "email": "team@example.com",
      "type": "team"
    }
  },
  {
    "owner": {
      "id": "usr-xxxxx",
      "name": "John Doe",
      "email": "john@example.com",
      "type": "user"
    }
  }
]
```

---

## Pagination

All list endpoints support cursor-based pagination:

```bash
# First page
curl "https://api.render.com/v1/services?limit=10" \
  -H "Authorization: Bearer $RENDER_API_KEY"

# Next page (use cursor from previous response)
curl "https://api.render.com/v1/services?limit=10&cursor=abc123" \
  -H "Authorization: Bearer $RENDER_API_KEY"
```

## Filtering

Most list endpoints support filtering via query parameters. Multiple values can be provided as arrays:

```bash
# Filter by multiple types
curl "https://api.render.com/v1/services?type=web_service&type=static_site" \
  -H "Authorization: Bearer $RENDER_API_KEY"

# Filter by date range
curl "https://api.render.com/v1/services?createdAfter=2024-01-01T00:00:00Z" \
  -H "Authorization: Bearer $RENDER_API_KEY"
```

## Error Responses

```json
{
  "id": "error-id",
  "message": "Error description"
}
```

Common error codes:
- `400`: Invalid request parameters
- `401`: Missing or invalid API key
- `403`: Insufficient permissions
- `404`: Resource not found
- `409`: Conflict (e.g., duplicate name)
- `422`: Unprocessable entity
- `429`: Rate limit exceeded
- `500`: Internal server error
