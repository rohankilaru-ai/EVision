#!/bin/bash
# EVision Application Test Script

echo "=================================="
echo "EVision Application Test Suite"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0

# Test function
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected="$3"

    echo -n "Testing $name... "
    response=$(curl -s "$url")

    if echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "  Expected to find: $expected"
        ((FAILED++))
        return 1
    fi
}

# Test HTTP status codes
test_status() {
    local name="$1"
    local url="$2"
    local expected_code="$3"

    echo -n "Testing $name... "
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "$url")

    if [ "$status_code" = "$expected_code" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $status_code)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (Expected $expected_code, got $status_code)"
        ((FAILED++))
        return 1
    fi
}

echo "=== Backend API Tests ==="
echo ""

test_status "Backend Root" "http://localhost:8000" "200"
test_endpoint "Backend Root Message" "http://localhost:8000" "Welcome to EVision API"
test_status "Health Check" "http://localhost:8000/health" "200"
test_endpoint "Health Status" "http://localhost:8000/health" '"status":"healthy"'
test_status "API Documentation" "http://localhost:8000/docs" "200"
test_endpoint "Swagger UI" "http://localhost:8000/docs" "swagger-ui"

echo ""
echo "=== Frontend Tests ==="
echo ""

test_status "Homepage" "http://localhost:3000" "200"
test_endpoint "Homepage Title" "http://localhost:3000" "EVision"
test_endpoint "Homepage CTA" "http://localhost:3000" "Get Started Free"
test_endpoint "Homepage Content" "http://localhost:3000" "Real-Time Analysis"
test_status "Login Page" "http://localhost:3000/login" "200"
test_endpoint "Login Page Title" "http://localhost:3000/login" "Sign in to find +EV opportunities"
test_endpoint "Login Page Button" "http://localhost:3000/login" "Sign in with Google"

echo ""
echo "=== API Endpoints Tests ==="
echo ""

# Test unauthenticated access (should return 401 or 403)
echo -n "Testing Protected Endpoint (should be protected)... "
status_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/v1/markets/ev-opportunities")
if [ "$status_code" = "401" ] || [ "$status_code" = "403" ] || [ "$status_code" = "422" ]; then
    echo -e "${GREEN}✓ PASSED${NC} (Properly protected - HTTP $status_code)"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ WARNING${NC} (Expected 401/403, got $status_code)"
fi

echo ""
echo "=== Link Navigation Tests ==="
echo ""

# Test that links are present in HTML
echo -n "Testing Login Link Presence... "
if curl -s "http://localhost:3000" | grep -q 'href="/login"'; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# Test that clicking login link would work (check destination)
echo -n "Testing Login Link Destination... "
if curl -s "http://localhost:3000/login" | grep -q "Sign in with Google"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

echo ""
echo "=== JavaScript & CSS Tests ==="
echo ""

# Check if JS and CSS are loading
echo -n "Testing JavaScript Loading... "
if curl -s "http://localhost:3000" | grep -q "_next/static/chunks"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

echo -n "Testing CSS Loading... "
if curl -s "http://localhost:3000" | grep -q "stylesheet"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

echo ""
echo "=================================="
echo "Test Results"
echo "=================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    echo ""
    echo "Your EVision app is running correctly!"
    echo ""
    echo "To access the app:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Backend:  http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi
