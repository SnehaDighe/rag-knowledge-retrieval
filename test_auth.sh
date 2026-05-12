#!/bin/bash

# Test script for RAG Knowledge Retrieval Authentication System
echo "🧪 Testing RAG Knowledge Retrieval Authentication System"
echo "======================================================"

BASE_URL="http://localhost:3000"

echo ""
echo "1. Testing signup..."
SIGNUP_RESPONSE=$(curl -s -X POST $BASE_URL/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "demo_user", "password": "demo_pass123"}')

echo "Signup Response: $SIGNUP_RESPONSE"

echo ""
echo "2. Testing login..."
LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo_user", "password": "demo_pass123"}')

echo "Login Response: $LOGIN_RESPONSE"

# Extract token from login response
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo ""
echo "3. Testing protected status endpoint..."
STATUS_RESPONSE=$(curl -s -X GET $BASE_URL/api/status \
  -H "Authorization: Bearer $TOKEN")

echo "Status Response: $STATUS_RESPONSE"

echo ""
echo "4. Testing token verification..."
VERIFY_RESPONSE=$(curl -s -X GET $BASE_URL/auth/verify \
  -H "Authorization: Bearer $TOKEN")

echo "Verify Response: $VERIFY_RESPONSE"

echo ""
echo "5. Testing unauthorized access..."
UNAUTH_RESPONSE=$(curl -s -X GET $BASE_URL/api/status)
echo "Unauthorized Response: $UNAUTH_RESPONSE"

echo ""
echo "✅ Authentication testing complete!"