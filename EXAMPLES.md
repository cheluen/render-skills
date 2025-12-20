# Render API Examples

Practical examples for common Render API operations.

## Table of Contents

1. [Service Management](#service-management)
2. [Deployment Workflows](#deployment-workflows)
3. [Database Operations](#database-operations)
4. [Monitoring & Debugging](#monitoring--debugging)
5. [Infrastructure Automation](#infrastructure-automation)
6. [CI/CD Integration](#cicd-integration)

---

## Service Management

### List All Services with Details

```bash
#!/bin/bash
# List all services with formatted output

curl -s "https://api.render.com/v1/services?limit=100" \
  -H "Authorization: Bearer $RENDER_API_KEY" | \
  jq -r '.[] | "\(.service.name)\t\(.service.type)\t\(.service.serviceDetails.region)\t\(.service.suspended)"'
```

### Find Service by Name

```bash
#!/bin/bash
# Find a service by name and return its ID

SERVICE_NAME="my-app"

curl -s "https://api.render.com/v1/services?name=$SERVICE_NAME" \
  -H "Authorization: Bearer $RENDER_API_KEY" | \
  jq -r '.[] | select(.service.name=="'"$SERVICE_NAME"'") | .service.id'
```

### Create a New Web Service

```bash
#!/bin/bash
# Create a Node.js web service

curl -X POST "https://api.render.com/v1/services" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "web_service",
    "name": "my-nodejs-app",
    "ownerId": "'"$RENDER_OWNER_ID"'",
    "repo": "https://github.com/username/repo",
    "autoDeploy": "yes",
    "branch": "main",
    "serviceDetails": {
      "env": "node",
      "region": "oregon",
      "plan": "starter",
      "buildCommand": "npm ci",
      "startCommand": "npm start",
      "envVars": [
        {"key": "NODE_ENV", "value": "production"},
        {"key": "PORT", "value": "10000"}
      ],
      "healthCheckPath": "/health"
    }
  }'
```

### Create a Static Site

```bash
#!/bin/bash
# Create a React static site

curl -X POST "https://api.render.com/v1/services" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "static_site",
    "name": "my-react-app",
    "ownerId": "'"$RENDER_OWNER_ID"'",
    "repo": "https://github.com/username/react-app",
    "autoDeploy": "yes",
    "branch": "main",
    "serviceDetails": {
      "buildCommand": "npm ci && npm run build",
      "publishPath": "build",
      "pullRequestPreviewsEnabled": "yes"
    }
  }'
```

### Scale Service Instances

```bash
#!/bin/bash
# Scale a service to 3 instances

SERVICE_ID="srv-xxxxx"

curl -X POST "https://api.render.com/v1/services/$SERVICE_ID/scale" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"numInstances": 3}'
```

### Configure Autoscaling

```bash
#!/bin/bash
# Enable autoscaling with CPU and memory triggers

SERVICE_ID="srv-xxxxx"

curl -X PUT "https://api.render.com/v1/services/$SERVICE_ID/autoscaling" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "min": 1,
    "max": 10,
    "criteria": {
      "cpu": {"enabled": true, "percentage": 70},
      "memory": {"enabled": true, "percentage": 80}
    }
  }'
```

### Suspend All Non-Production Services

```bash
#!/bin/bash
# Suspend services that match a pattern (e.g., staging, dev)

for SERVICE_ID in $(curl -s "https://api.render.com/v1/services?name=staging" \
  -H "Authorization: Bearer $RENDER_API_KEY" | \
  jq -r '.[].service.id'); do
    echo "Suspending $SERVICE_ID..."
    curl -X POST "https://api.render.com/v1/services/$SERVICE_ID/suspend" \
      -H "Authorization: Bearer $RENDER_API_KEY"
done
```

---

## Deployment Workflows

### Deploy with Cache Clear

```bash
#!/bin/bash
# Trigger a deploy with cache clear

SERVICE_ID="srv-xxxxx"

DEPLOY=$(curl -X POST "https://api.render.com/v1/services/$SERVICE_ID/deploys" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"clearCache": "clear"}')

echo "Deploy triggered: $(echo $DEPLOY | jq -r '.id')"
```

### Wait for Deploy to Complete

```bash
#!/bin/bash
# Deploy and wait for completion

SERVICE_ID="srv-xxxxx"
MAX_WAIT=600  # 10 minutes

# Trigger deploy
DEPLOY_ID=$(curl -s -X POST "https://api.render.com/v1/services/$SERVICE_ID/deploys" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"clearCache": "do_not_clear"}' | jq -r '.id')

echo "Deploy started: $DEPLOY_ID"

# Poll for status
START_TIME=$(date +%s)
while true; do
    STATUS=$(curl -s "https://api.render.com/v1/services/$SERVICE_ID/deploys/$DEPLOY_ID" \
      -H "Authorization: Bearer $RENDER_API_KEY" | jq -r '.status')

    echo "Status: $STATUS"

    case $STATUS in
        "live")
            echo "Deploy succeeded!"
            exit 0
            ;;
        "build_failed"|"update_failed"|"canceled")
            echo "Deploy failed: $STATUS"
            exit 1
            ;;
    esac

    ELAPSED=$(($(date +%s) - START_TIME))
    if [ $ELAPSED -ge $MAX_WAIT ]; then
        echo "Timeout waiting for deploy"
        exit 1
    fi

    sleep 10
done
```

### Rollback to Previous Deploy

```bash
#!/bin/bash
# Rollback to the previous successful deploy

SERVICE_ID="srv-xxxxx"

# Get the last successful deploy (skip current)
PREVIOUS_DEPLOY=$(curl -s "https://api.render.com/v1/services/$SERVICE_ID/deploys?limit=10" \
  -H "Authorization: Bearer $RENDER_API_KEY" | \
  jq -r '[.[] | select(.deploy.status=="deactivated")] | .[0].deploy.id')

if [ "$PREVIOUS_DEPLOY" != "null" ] && [ -n "$PREVIOUS_DEPLOY" ]; then
    echo "Rolling back to: $PREVIOUS_DEPLOY"
    curl -X POST "https://api.render.com/v1/services/$SERVICE_ID/rollback" \
      -H "Authorization: Bearer $RENDER_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"deployId": "'"$PREVIOUS_DEPLOY"'"}'
else
    echo "No previous deploy found"
    exit 1
fi
```

### Deploy Multiple Services

```bash
#!/bin/bash
# Deploy multiple services in parallel

SERVICES=("srv-xxxxx" "srv-yyyyy" "srv-zzzzz")

for SERVICE_ID in "${SERVICES[@]}"; do
    (
        echo "Deploying $SERVICE_ID..."
        curl -s -X POST "https://api.render.com/v1/services/$SERVICE_ID/deploys" \
          -H "Authorization: Bearer $RENDER_API_KEY" \
          -H "Content-Type: application/json" \
          -d '{"clearCache": "do_not_clear"}' > /dev/null
        echo "Deploy triggered for $SERVICE_ID"
    ) &
done

wait
echo "All deploys triggered"
```

---

## Database Operations

### Create Postgres Database

```bash
#!/bin/bash
# Create a new Postgres database

curl -X POST "https://api.render.com/v1/postgres" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-database",
    "ownerId": "'"$RENDER_OWNER_ID"'",
    "region": "oregon",
    "plan": "starter",
    "version": "15",
    "databaseName": "appdb",
    "databaseUser": "appuser"
  }'
```

### Get Database Connection String

```bash
#!/bin/bash
# Get external connection string for a database

POSTGRES_ID="dpg-xxxxx"

curl -s "https://api.render.com/v1/postgres/$POSTGRES_ID/connection-info" \
  -H "Authorization: Bearer $RENDER_API_KEY" | \
  jq -r '.externalConnectionString'
```

### Backup Database Before Maintenance

```bash
#!/bin/bash
# Export database info before operations

POSTGRES_ID="dpg-xxxxx"
BACKUP_FILE="db-backup-$(date +%Y%m%d-%H%M%S).json"

# Get current state
curl -s "https://api.render.com/v1/postgres/$POSTGRES_ID" \
  -H "Authorization: Bearer $RENDER_API_KEY" > "$BACKUP_FILE"

# Get connection info
curl -s "https://api.render.com/v1/postgres/$POSTGRES_ID/connection-info" \
  -H "Authorization: Bearer $RENDER_API_KEY" | \
  jq -r '.psqlCommand' >> "$BACKUP_FILE"

echo "Backup saved to $BACKUP_FILE"
```

### Create Redis Cache

```bash
#!/bin/bash
# Create a Key Value (Redis) instance

curl -X POST "https://api.render.com/v1/key-value" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-cache",
    "ownerId": "'"$RENDER_OWNER_ID"'",
    "region": "oregon",
    "plan": "starter",
    "maxmemoryPolicy": "allkeys-lru"
  }'
```

---

## Monitoring & Debugging

### Fetch Recent Logs

```bash
#!/bin/bash
# Get last 100 log entries for a service

SERVICE_ID="srv-xxxxx"

curl -s "https://api.render.com/v1/logs?resource=$SERVICE_ID&limit=100" \
  -H "Authorization: Bearer $RENDER_API_KEY" | \
  jq -r '.logs[] | "\(.timestamp) [\(.level)] \(.message)"'
```

### Fetch Error Logs Only

```bash
#!/bin/bash
# Get only error-level logs

SERVICE_ID="srv-xxxxx"
START_TIME=$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ)

curl -s "https://api.render.com/v1/logs?resource=$SERVICE_ID&level=error&startTime=$START_TIME" \
  -H "Authorization: Bearer $RENDER_API_KEY" | \
  jq -r '.logs[] | "\(.timestamp) \(.message)"'
```

### Monitor Build Logs

```bash
#!/bin/bash
# Get build logs for a specific deploy

SERVICE_ID="srv-xxxxx"
DEPLOY_ID="dep-xxxxx"

curl -s "https://api.render.com/v1/logs?resource=$SERVICE_ID&type=build&limit=500" \
  -H "Authorization: Bearer $RENDER_API_KEY" | \
  jq -r '.logs[] | .message'
```

### Check HTTP Request Logs

```bash
#!/bin/bash
# Get HTTP request logs with 5xx errors

SERVICE_ID="srv-xxxxx"

curl -s "https://api.render.com/v1/logs?resource=$SERVICE_ID&type=request&statusCode=5*" \
  -H "Authorization: Bearer $RENDER_API_KEY" | \
  jq -r '.logs[] | "\(.timestamp) \(.statusCode) \(.method) \(.path)"'
```

### Real-time Log Streaming

```bash
#!/bin/bash
# Stream logs in real-time using SSE

SERVICE_ID="srv-xxxxx"

curl -N "https://api.render.com/v1/logs/subscribe?resource=$SERVICE_ID" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Accept: text/event-stream"
```

---

## Infrastructure Automation

### Sync All Blueprints

```bash
#!/bin/bash
# Trigger sync for all blueprints

for BLUEPRINT_ID in $(curl -s "https://api.render.com/v1/blueprints" \
  -H "Authorization: Bearer $RENDER_API_KEY" | \
  jq -r '.[].blueprint.id'); do
    echo "Syncing blueprint: $BLUEPRINT_ID"
    curl -X POST "https://api.render.com/v1/blueprints/$BLUEPRINT_ID/sync" \
      -H "Authorization: Bearer $RENDER_API_KEY"
done
```

### Bulk Update Environment Variables

```bash
#!/bin/bash
# Update env vars across multiple services

SERVICES=("srv-xxxxx" "srv-yyyyy")
NEW_ENV_VARS='[
  {"key": "LOG_LEVEL", "value": "info"},
  {"key": "FEATURE_FLAG_X", "value": "true"}
]'

for SERVICE_ID in "${SERVICES[@]}"; do
    echo "Updating env vars for $SERVICE_ID..."

    # Get current env vars
    CURRENT=$(curl -s "https://api.render.com/v1/services/$SERVICE_ID/env-vars" \
      -H "Authorization: Bearer $RENDER_API_KEY" | \
      jq '[.[].envVar | {key, value}]')

    # Merge with new vars
    MERGED=$(echo "$CURRENT $NEW_ENV_VARS" | jq -s 'add | unique_by(.key)')

    # Update
    curl -X PUT "https://api.render.com/v1/services/$SERVICE_ID/env-vars" \
      -H "Authorization: Bearer $RENDER_API_KEY" \
      -H "Content-Type: application/json" \
      -d "$MERGED"
done
```

### Add Custom Domain and Verify

```bash
#!/bin/bash
# Add a custom domain and wait for verification

SERVICE_ID="srv-xxxxx"
DOMAIN="api.example.com"

# Add domain
RESULT=$(curl -s -X POST "https://api.render.com/v1/services/$SERVICE_ID/custom-domains" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "'"$DOMAIN"'"}')

DOMAIN_ID=$(echo "$RESULT" | jq -r '.id')
echo "Domain added: $DOMAIN_ID"

# Check verification status
for i in {1..12}; do
    STATUS=$(curl -s "https://api.render.com/v1/services/$SERVICE_ID/custom-domains/$DOMAIN_ID" \
      -H "Authorization: Bearer $RENDER_API_KEY" | \
      jq -r '.verificationStatus')

    echo "Verification status: $STATUS"

    if [ "$STATUS" = "verified" ]; then
        echo "Domain verified!"
        exit 0
    fi

    # Trigger verification check
    curl -s -X POST "https://api.render.com/v1/services/$SERVICE_ID/custom-domains/$DOMAIN_ID/verify" \
      -H "Authorization: Bearer $RENDER_API_KEY" > /dev/null

    sleep 30
done

echo "Verification pending - check DNS settings"
```

### Run Database Migration Job

```bash
#!/bin/bash
# Run a one-off migration job

SERVICE_ID="srv-xxxxx"

# Create the job
JOB_RESULT=$(curl -s -X POST "https://api.render.com/v1/services/$SERVICE_ID/jobs" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "startCommand": "npm run db:migrate",
    "planOverride": "standard"
  }')

JOB_ID=$(echo "$JOB_RESULT" | jq -r '.id')
echo "Job created: $JOB_ID"

# Wait for completion
while true; do
    STATUS=$(curl -s "https://api.render.com/v1/services/$SERVICE_ID/jobs/$JOB_ID" \
      -H "Authorization: Bearer $RENDER_API_KEY" | jq -r '.status')

    echo "Job status: $STATUS"

    case $STATUS in
        "succeeded")
            echo "Migration completed successfully!"
            exit 0
            ;;
        "failed"|"canceled")
            echo "Job failed: $STATUS"
            exit 1
            ;;
    esac

    sleep 5
done
```

---

## CI/CD Integration

### GitHub Actions Deployment

```yaml
# .github/workflows/deploy.yml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Render Deploy
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
          SERVICE_ID: ${{ secrets.RENDER_SERVICE_ID }}
        run: |
          DEPLOY_RESPONSE=$(curl -s -X POST \
            "https://api.render.com/v1/services/$SERVICE_ID/deploys" \
            -H "Authorization: Bearer $RENDER_API_KEY" \
            -H "Content-Type: application/json" \
            -d '{"clearCache": "do_not_clear"}')

          DEPLOY_ID=$(echo $DEPLOY_RESPONSE | jq -r '.id')
          echo "Deploy ID: $DEPLOY_ID"

          # Wait for deploy
          for i in {1..60}; do
            STATUS=$(curl -s \
              "https://api.render.com/v1/services/$SERVICE_ID/deploys/$DEPLOY_ID" \
              -H "Authorization: Bearer $RENDER_API_KEY" | jq -r '.status')

            echo "Status: $STATUS"

            if [ "$STATUS" = "live" ]; then
              echo "Deploy succeeded!"
              exit 0
            elif [ "$STATUS" = "build_failed" ] || [ "$STATUS" = "update_failed" ]; then
              echo "Deploy failed!"
              exit 1
            fi

            sleep 10
          done

          echo "Deploy timeout"
          exit 1
```

### GitLab CI Integration

```yaml
# .gitlab-ci.yml
deploy_to_render:
  stage: deploy
  only:
    - main
  script:
    - |
      DEPLOY_ID=$(curl -s -X POST \
        "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys" \
        -H "Authorization: Bearer $RENDER_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"clearCache": "do_not_clear"}' | jq -r '.id')

      echo "Triggered deploy: $DEPLOY_ID"

      while true; do
        STATUS=$(curl -s \
          "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys/$DEPLOY_ID" \
          -H "Authorization: Bearer $RENDER_API_KEY" | jq -r '.status')

        case $STATUS in
          "live") echo "Success!"; exit 0 ;;
          "build_failed"|"update_failed") echo "Failed!"; exit 1 ;;
        esac

        sleep 10
      done
```

### Terraform-like Resource Export

```bash
#!/bin/bash
# Export all services as JSON for infrastructure-as-code

OUTPUT_DIR="render-export-$(date +%Y%m%d)"
mkdir -p "$OUTPUT_DIR"

# Export services
curl -s "https://api.render.com/v1/services?limit=100" \
  -H "Authorization: Bearer $RENDER_API_KEY" > "$OUTPUT_DIR/services.json"

# Export databases
curl -s "https://api.render.com/v1/postgres" \
  -H "Authorization: Bearer $RENDER_API_KEY" > "$OUTPUT_DIR/postgres.json"

# Export key-value stores
curl -s "https://api.render.com/v1/key-value" \
  -H "Authorization: Bearer $RENDER_API_KEY" > "$OUTPUT_DIR/key-value.json"

# Export blueprints
curl -s "https://api.render.com/v1/blueprints" \
  -H "Authorization: Bearer $RENDER_API_KEY" > "$OUTPUT_DIR/blueprints.json"

echo "Export complete: $OUTPUT_DIR"
ls -la "$OUTPUT_DIR"
```

---

## Helper Functions

### Bash Function Library

```bash
# render-functions.sh
# Source this file: source render-functions.sh

render_api() {
    local method="${1:-GET}"
    local endpoint="$2"
    local data="$3"

    if [ -z "$RENDER_API_KEY" ]; then
        echo "Error: RENDER_API_KEY not set" >&2
        return 1
    fi

    local args=(-s -X "$method" "https://api.render.com/v1$endpoint")
    args+=(-H "Authorization: Bearer $RENDER_API_KEY")
    args+=(-H "Accept: application/json")

    if [ -n "$data" ]; then
        args+=(-H "Content-Type: application/json")
        args+=(-d "$data")
    fi

    curl "${args[@]}"
}

render_list_services() {
    render_api GET "/services?limit=100" | jq -r '.[].service | "\(.id)\t\(.name)\t\(.type)"'
}

render_get_service() {
    render_api GET "/services/$1"
}

render_deploy() {
    render_api POST "/services/$1/deploys" '{"clearCache": "do_not_clear"}'
}

render_suspend() {
    render_api POST "/services/$1/suspend"
}

render_resume() {
    render_api POST "/services/$1/resume"
}

render_logs() {
    local service_id="$1"
    local limit="${2:-50}"
    render_api GET "/logs?resource=$service_id&limit=$limit" | jq -r '.logs[] | "\(.timestamp) [\(.level)] \(.message)"'
}
```

### Usage Example

```bash
source render-functions.sh

# List all services
render_list_services

# Deploy a service
render_deploy srv-xxxxx

# Get logs
render_logs srv-xxxxx 100
```
