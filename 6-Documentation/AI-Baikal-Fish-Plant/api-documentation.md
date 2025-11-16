# API Documentation
## Baikal Fish Processing Plant Digital System

## Base Information

**Base URL:** `https://api.baikal-fish.ru/v1`

**Authentication:** Bearer Token
**Rate Limit:** 1000 requests per hour per API key

## Authentication

### Get Access Token

```http
POST /auth/token
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
