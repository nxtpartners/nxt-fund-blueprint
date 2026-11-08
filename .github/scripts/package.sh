#!/usr/bin/env bash
# Builds the plugin zip for a private upload to claude.ai (Customize > Plugins > Add > Upload plugin).
set -euo pipefail
cd "$(dirname "$0")/../.."
find skills -name '__pycache__' -type d -prune -exec rm -rf {} +
version=$(python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['version'])")
out="dist/nxt-fund-blueprint-$version.zip"
mkdir -p dist && rm -f dist/nxt-fund-blueprint-*.zip   # keep only the current build
zip -qr "$out" .claude-plugin skills README.md LICENSE -x '*/.DS_Store'
echo "$out"
