#!/bin/bash
# Quick sync script for BSI Dashboard
cd /Users/cutterkates/Documents/GitHub/BSI-Dashboard
git add -A
git commit -m "Update: $(date '+%Y-%m-%d %H:%M')"
git push
echo "✓ Synced to GitHub"
