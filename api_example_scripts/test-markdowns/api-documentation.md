# API Documentation

## Agent Orchestration API Reference

### Base URL
```
https://api.agent-orchestration.com/v1
```

### Authentication
All API requests require authentication using an API key in the header:
```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Sessions

#### Create Session
```http
POST /sessions
Content-Type: application/json

{
  "name": "My Session",
  "description": "Session description",
  "config": {
    "timeout": 3600,
    "max_iterations": 100
  }
}
```

**Response:**
```json
{
  "id": "session_123",
  "name": "My Session",
  "status": "created",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Get Session
```http
GET /sessions/{session_id}
```

#### List Sessions
```http
GET /sessions?limit=10&offset=0
```

### Agents

#### Deploy Agent
```http
POST /agents
Content-Type: application/json

{
  "name": "Data Processor",
  "type": "python",
  "code": "def process_data(data): return data.upper()",
  "requirements": ["pandas", "numpy"]
}
```

#### Execute Agent
```http
POST /agents/{agent_id}/execute
Content-Type: application/json

{
  "input_data": {"text": "hello world"},
  "session_id": "session_123"
}
```

### Knowledge Base

#### Upload Document
```http
POST /knowledge/documents
Content-Type: multipart/form-data

file: [binary file data]
metadata: {"title": "Document Title", "tags": ["tag1", "tag2"]}
```

#### Search Knowledge
```http
GET /knowledge/search?q=query&limit=10
```

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request is invalid",
    "details": {
      "field": "name",
      "issue": "required field missing"
    }
  }
}
```

### Common Error Codes
- `INVALID_REQUEST` (400): Request validation failed
- `UNAUTHORIZED` (401): Invalid or missing API key
- `NOT_FOUND` (404): Resource not found
- `RATE_LIMITED` (429): Too many requests
- `INTERNAL_ERROR` (500): Server error

## Rate Limits
- 1000 requests per hour per API key
- 10 concurrent sessions per account
- 100MB file upload limit

## SDKs and Examples
- Python SDK: `pip install agent-orchestration-sdk`
- JavaScript SDK: `npm install @agent-orch/sdk`
- Example scripts available in the `examples/` directory

## Webhooks
Configure webhooks to receive real-time updates:
```http
POST /webhooks
Content-Type: application/json

{
  "url": "https://your-app.com/webhook",
  "events": ["session.completed", "agent.failed"]
}
```

## Support
- Documentation: https://docs.agent-orchestration.com
- Support: support@agent-orchestration.com
- Status Page: https://status.agent-orchestration.com
