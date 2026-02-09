#!/usr/bin/env python3
"""
Simple MCP connection test using SSE
"""

import sys
import time
import subprocess

print("Testing MCP Server Connection...")
print("-" * 50)

# Test 1: Check if server is running
print("\n1. Checking if server is running...")
result = subprocess.run(["lsof", "-i", ":9001"], capture_output=True, text=True)
if result.returncode == 0:
    print("   ✅ Server is running on port 9001")
else:
    print("   ❌ Server is NOT running on port 9001")
    sys.exit(1)

# Test 2: Test SSE endpoint
print("\n2. Testing SSE endpoint...")
result = subprocess.run(["curl", "-s", "http://localhost:9001/sse", "--max-time", "2"],
                       capture_output=True, text=True)
if "event: endpoint" in result.stdout:
    print("   ✅ SSE endpoint responding")
    # Extract session ID
    for line in result.stdout.split('\n'):
        if line.startswith('data:'):
            messages_url = line.split('data: ')[1]
            print(f"   ✅ Messages URL: {messages_url}")
            break
else:
    print("   ❌ SSE endpoint not responding correctly")
    print(f"   Output: {result.stdout}")
    sys.exit(1)

print("\n" + "=" * 50)
print("✅ MCP Server is responding correctly")
print("=" * 50)
print("\nIf Claude still can't connect, the issue may be:")
print("  1. Claude's MCP client implementation")
print("  2. Protocol version mismatch")
print("  3. Missing MCP methods or resources")
print("  4. Server configuration issues")
print("\nTry:")
print("  - Completely restart Claude")
print("  - Check Claude's logs for MCP errors")
print("  - Verify mcpServers config in ~/.claude.json")
