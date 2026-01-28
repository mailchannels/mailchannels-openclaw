#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="mailchannels-email-api"
SLUG="mailchannels-email-api"
VERSION="1.0.0"

# Ensure CLI is installed
if ! command -v clawdhub >/dev/null 2>&1; then
  echo "clawdhub CLI not found. Install with: npm install -g clawdhub" >&2
  exit 1
fi

# Ensure logged in
if ! clawdhub whoami >/dev/null 2>&1; then
  echo "Not logged in. Run: clawdhub login" >&2
  exit 1
fi

# Publish
clawdhub publish "./${SKILL_DIR}" --slug "${SLUG}" --version "${VERSION}"
