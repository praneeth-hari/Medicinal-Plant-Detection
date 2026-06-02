# 🚀 Deployment Guide

> **Status:** Stub — deployment procedures will be documented as infrastructure is finalized.

## Overview

This guide covers deploying the Medicinal Plant Detection & RAG Assistant to a production environment.

## Deployment Options

### 1. Docker Compose (Recommended for small deployments)

```bash
# Build and start all services
docker-compose -f docker-compose.yml up --build -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f
```

### 2. Cloud Deployment

<!-- TODO: Add cloud-specific deployment instructions -->

- **AWS**: ECS/Fargate, RDS, S3
- **GCP**: Cloud Run, Cloud SQL, GCS
- **Azure**: Container Apps, Azure SQL, Blob Storage

### 3. Kubernetes

<!-- TODO: Add Kubernetes manifests and Helm charts -->

## Pre-deployment Checklist

- [ ] Set all production environment variables
- [ ] Run database migrations
- [ ] Build and test Docker images locally
- [ ] Configure SSL/TLS certificates
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy for database
- [ ] Load trained ML model into production model directory

## Environment Variables

See `deployment/.env.production.example` for the full list of required variables.

## Monitoring

<!-- TODO: Add monitoring setup (Prometheus, Grafana, etc.) -->

## Rollback Procedure

<!-- TODO: Document rollback steps -->
