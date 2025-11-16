#!/bin/bash

# Profile Settings Test Script using cURL
# Usage: ./test_profile_curl.sh

BASE_URL="http://localhost:8000/api/v1"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Profile Settings Test Script${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if email and password are provided
if [ -z "$1" ] || [ -z "$2" ]; then
    echo -e "${YELLOW}Usage: $0 <email> <password>${NC}"
    echo -e "${YELLOW}Example: $0 user@example.com password123${NC}"
    exit 1
fi

EMAIL=$1
PASSWORD=$2

echo -e "${BLUE}Step 1: Login${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/auth/login/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\",
    \"remember_me\": false
  }")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}✗ Login failed${NC}"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ Login successful${NC}"
echo -e "Token: ${TOKEN:0:20}...\n"

echo -e "${BLUE}Step 2: Get Current Profile${NC}"
PROFILE_RESPONSE=$(curl -s -X GET "$BASE_URL/auth/user/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

echo "$PROFILE_RESPONSE" | python3 -m json.tool
echo ""

echo -e "${BLUE}Step 3: Update Profile${NC}"
UPDATE_RESPONSE=$(curl -s -X PATCH "$BASE_URL/auth/user/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "User",
    "phone_number": "+1234567890",
    "bio": "This is a test bio from curl script",
    "country": "US",
    "state": "California"
  }')

echo "$UPDATE_RESPONSE" | python3 -m json.tool
echo ""

echo -e "${BLUE}Step 4: Verify Update${NC}"
VERIFY_RESPONSE=$(curl -s -X GET "$BASE_URL/auth/user/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

echo "$VERIFY_RESPONSE" | python3 -m json.tool
echo ""

echo -e "${BLUE}Step 5: Get Profile Update Requests${NC}"
REQUESTS_RESPONSE=$(curl -s -X GET "$BASE_URL/users/profile-update-requests/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

echo "$REQUESTS_RESPONSE" | python3 -m json.tool
echo ""

echo -e "${GREEN}✓ All tests completed${NC}"

