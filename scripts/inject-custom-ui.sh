#!/bin/bash
# ==========================================================================
# Sentinel Plane Custom UI Injector Script
# Injects the <link> tag for custom-ui.css into running Nginx containers.
# ==========================================================================

set -euo pipefail

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== Injecting Sentinel Custom UI Stylesheets ===${NC}"

# 1. Inject into Frontend Container (plane-app-web-1)
if docker ps --format '{{.Names}}' | grep -q 'plane-app-web-1'; then
    echo "Processing Frontend (web)..."
    # Check if link tag is already present in index.html
    if docker exec plane-app-web-1 grep -q "custom-ui.css" /usr/share/nginx/html/index.html 2>/dev/null; then
        echo -e "${GREEN}  ✅ Frontend index.html already has custom-ui.css. Skipping.${NC}"
    else
        echo "  Injecting custom-ui.css link tag..."
        docker exec plane-app-web-1 sed -i 's|</head>|<link rel="stylesheet" href="/custom-ui.css"></head>|g' /usr/share/nginx/html/index.html
        echo -e "${GREEN}  ✅ Injection successful in Frontend.${NC}"
    fi
else
    echo -e "${RED}  ❌ Frontend container plane-app-web-1 is not running.${NC}"
fi

# 2. Inject into Admin Container (plane-app-admin-1)
if docker ps --format '{{.Names}}' | grep -q 'plane-app-admin-1'; then
    echo "Processing God-Mode Admin Panel..."
    # Check if link tag is already present in god-mode index.html
    if docker exec plane-app-admin-1 grep -q "custom-ui.css" /usr/share/nginx/html/god-mode/index.html 2>/dev/null; then
        echo -e "${GREEN}  ✅ God-Mode index.html already has custom-ui.css. Skipping.${NC}"
    else
        echo "  Injecting custom-ui.css link tag..."
        docker exec plane-app-admin-1 sed -i 's|</head>|<link rel="stylesheet" href="/custom-ui.css"></head>|g' /usr/share/nginx/html/god-mode/index.html
        echo -e "${GREEN}  ✅ Injection successful in God-Mode.${NC}"
    fi
else
    echo -e "${RED}  ❌ Admin container plane-app-admin-1 is not running.${NC}"
fi

echo -e "${BLUE}=== Injection Process Completed ===${NC}"
