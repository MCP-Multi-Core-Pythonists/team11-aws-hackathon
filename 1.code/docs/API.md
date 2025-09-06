# Sync Hub API Documentation

## Overview

The Sync Hub API provides endpoints for managing VS Code settings synchronization across multiple devices and teams.

- **Base URL:** `https://l7ycatge3j.execute-api.us-east-1.amazonaws.com`
- **Authentication:** JWT Bearer tokens from Cognito
- **Authorization:** `https://sync-hub-851725240440.auth.us-east-1.amazoncognito.com`

## Interactive Documentation

- **Swagger UI:** [https://d1iz4bwpzq14da.cloudfront.net/docs/](https://d1iz4bwpzq14da.cloudfront.net/docs/)
- **OpenAPI Spec:** [https://d1iz4bwpzq14da.cloudfront.net/docs/openapi.json](https://d1iz4bwpzq14da.cloudfront.net/docs/openapi.json)

## Authentication

All endpoints (except `/_health` and `/settings/public`) require a JWT Bearer token:

```bash
Authorization: Bearer <your-jwt-token>
```

### Getting a Token

1. Visit the Hosted UI: `https://sync-hub-851725240440.auth.us-east-1.amazoncognito.com`
2. Sign in with Google
3. Extract the `id_token` from the callback

## Quick Start Examples

### Health Check (Public)
```bash
curl -X GET "https://l7ycatge3j.execute-api.us-east-1.amazonaws.com/_health"
```

### Create a Private Setting
```bash
curl -X POST "https://l7ycatge3j.execute-api.us-east-1.amazonaws.com/settings" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-vscode-config",
    "content": {"editor.fontSize": 16, "workbench.colorTheme": "Dark+"},
    "visibility": "private"
  }'
```

### List My Settings
```bash
curl -X GET "https://l7ycatge3j.execute-api.us-east-1.amazonaws.com/settings" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### List Public Settings (No Auth)
```bash
curl -X GET "https://l7ycatge3j.execute-api.us-east-1.amazonaws.com/settings/public"
```

### Get Setting History
```bash
curl -X GET "https://l7ycatge3j.execute-api.us-east-1.amazonaws.com/settings/SETTING_ID/history" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Rollback Setting
```bash
curl -X POST "https://l7ycatge3j.execute-api.us-east-1.amazonaws.com/settings/SETTING_ID/rollback" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"version": 2}'
```

### Create a Group
```bash
curl -X POST "https://l7ycatge3j.execute-api.us-east-1.amazonaws.com/groups" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Development Team",
    "description": "Shared settings for developers"
  }'
```

### Admin: Add Member to Group
```bash
curl -X POST "https://l7ycatge3j.execute-api.us-east-1.amazonaws.com/admin/groups/GROUP_ID/members" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "role": "member"
  }'
```

## Error Handling

All errors follow this format:

```json
{
  "error": "Error message",
  "detail": "Additional details (optional)",
  "request_id": "req_123456 (optional)"
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden (Admin required)
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limits

- **Authenticated requests:** 1000 requests per hour
- **Public endpoints:** 100 requests per hour per IP

## Support

For API support, contact: support@synchub.dev
