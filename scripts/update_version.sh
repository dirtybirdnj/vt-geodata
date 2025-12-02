#!/bin/bash
# Update version.json with current commit ID
# Run this before committing to ensure version is updated

COMMIT_ID=$(git rev-parse --short HEAD)
TIMESTAMP=$(date +%Y-%m-%d)

cat > docs/viewer/version.json << EOF
{
  "commitId": "${COMMIT_ID}",
  "timestamp": "${TIMESTAMP}"
}
EOF

echo "Updated version.json to commit ${COMMIT_ID}"
