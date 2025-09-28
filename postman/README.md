# HealthLogue AI Agents - API Testing with Postman

This directory contains Postman collections and environments for testing the AI Agents API.

## 📁 Files

- `AgentsAPI.postman_collection.json` - API collection with all endpoints
- `HealthLogue_AI_Agents_Environment.postman_environment.json` - Environment variables
- `README.md` - This file

## 🚀 Quick Start

### 1. Import Collection
1. Open Postman
2. Click "Import" button
3. Select `AgentsAPI.postman_collection.json`
4. Select `HealthLogue_AI_Agents_Environment.postman_environment.json`

### 2. Set Environment
1. Click the environment dropdown (top right)
2. Select "HealthLogue AI Agents Environment"
3. Verify variables are set correctly

### 3. Test API
1. Select any request from the collection
2. Click "Send"
3. Check the response

## 🌐 Environments

### Local Development
- **Base URL**: `http://localhost:7001`
- **Health Check**: `http://localhost:7001/health`
- **API Docs**: `http://localhost:7001/docs`

### Production (Heroku)
- **Base URL**: `https://ai-agents-alpha-797b03a63fa9.herokuapp.com`
- **Health Check**: `https://ai-agents-alpha-797b03a63fa9.herokuapp.com/health`
- **API Docs**: `https://ai-agents-alpha-797b03a63fa9.herokuapp.com/docs`

## 📋 Available Endpoints

### Health Check
- **GET** `/health`
- **Description**: Check if the service is running
- **Response**: `{"status": "running"}`

### Agent Chat
- **POST** `/api/agents/chat`
- **Description**: Chat with AI agents
- **Body**: JSON with agent_name, user_id, session_id, query, features

### Root
- **GET** `/`
- **Description**: Welcome message
- **Response**: `{"message": "Welcome to the HealthLogue AI Api!"}`

## 🔧 Environment Variables

### Base URLs
- `base_url` - Local development URL
- `base_url_production` - Production URL

### Test Data
- `user_id` - Test user ID (default: "user-123")
- `session_id` - Test session ID (default: "session-456")
- `agent_name` - Agent to test (default: "medical_followup")

## 📝 Sample Requests

### Health Check
```http
GET {{base_url}}/health
```

### Agent Chat - Medical Followup
```json
{
  "agent_name": "medical_followup_agent",
  "user_id": "user-123",
  "session_id": "session-456",
  "query": [
    {
      "speaker": "Patient",
      "text": "I have chest pain"
    },
    {
      "speaker": "Doctor", 
      "text": "Can you describe it?"
    },
    {
      "speaker": "Patient",
      "text": "It's a sharp, stabbing pain that started after lifting heavy boxes"
    }
  ],
  "features": [
    {
      "feature_name": "max_followups",
      "feature_value": 5
    }
  ]
}
```

## 🧪 Testing Scenarios

### 1. Basic Health Check
- Test if service is running
- Should return `{"status": "running"}`

### 2. Agent Chat - New Session
- Use a new session_id
- Should create new session and return followup questions

### 3. Agent Chat - Existing Session
- Use same session_id as previous request
- Should continue conversation and return followup questions

### 4. Error Handling
- Test with invalid agent_name
- Test with malformed request body
- Should return appropriate error messages

## 🔍 Troubleshooting

### Connection Refused
- Check if service is running locally: `curl http://localhost:7001/health`
- Verify environment variables are set correctly
- Check if port 7001 is available

### 404 Not Found
- Verify the endpoint URL is correct
- Check if the service is deployed properly
- Ensure the route exists in the API

### 500 Internal Server Error
- Check service logs for detailed error information
- Verify API keys are set correctly
- Check database connection if using persistent sessions

### Authentication Issues
- Verify API keys are valid and have sufficient credits
- Check if the service is configured correctly
- Ensure environment variables are set

## 📊 Response Examples

### Successful Health Check
```json
{
  "status": "running"
}
```

### Successful Agent Chat
```json
{
  "agent_name": "medical_followup_agent",
  "user_id": "user-123",
  "session_id": "session-456",
  "sender": "AGENT",
  "success": true,
  "agent_response": {
    "followup_questions": [
      "Have you experienced any shortness of breath?",
      "Did the pain radiate to your arm or jaw?",
      "Are you experiencing any nausea or sweating?"
    ],
    "count": 3
  }
}
```

### Error Response
```json
{
  "detail": "Agent 'invalid_agent' not found. Available agents: ['medical_followup_agent']"
}
```

## 🔄 Environment Switching

### Switch to Local
1. Select "HealthLogue AI Agents Environment"
2. Ensure `base_url` is set to `http://localhost:7001`
3. Make sure local service is running

### Switch to Production
1. Select "HealthLogue AI Agents Environment"
2. Change `base_url` to `https://ai-agents-alpha-797b03a63fa9.herokuapp.com`
3. Or use `base_url_production` variable

## 📚 Related Documentation

- [Main README](../README.md) - High-level architecture
- [Local Development](../LOCAL_DEVELOPMENT.md) - Local setup guide
- [Heroku Deployment](../service_cloud_deploy/heroku/README.md) - Production deployment
- [Database Setup](../agent_store_deploy/README.md) - Database configuration
