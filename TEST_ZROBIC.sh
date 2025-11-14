#!/bin/bash
# Test script for zrobić aspect detection

echo "Clearing Python cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

echo ""
echo "Running test for zrobić..."
echo "=================================="
python3 test_zrobic_aspect.py

