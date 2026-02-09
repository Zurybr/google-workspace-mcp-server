#!/usr/bin/env python3
"""
Test script for Google Workspace MCP Server
Tests MCP connection and basic operations
"""

import asyncio
import json
import httpx
import sys

async def test_mcp_connection():
    """Test MCP SSE connection and basic operations"""

    print("Testing Google Workspace MCP Server...")
    print("-" * 50)

    # Test 1: SSE Endpoint
    print("\n1. Testing SSE endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:9001/sse", timeout=5.0)
            if response.status_code == 200:
                print("   ✅ SSE endpoint: OK (200)")
                content = response.text
                if "event: endpoint" in content:
                    print("   ✅ SSE event format: OK")
                    # Extract session ID
                    for line in content.split('\n'):
                        if line.startswith('data:'):
                            messages_url = line.split('data: ')[1]
                            print(f"   ✅ Messages endpoint: {messages_url}")
                            break
                else:
                    print("   ❌ SSE event format: FAILED")
                    return False
            else:
                print(f"   ❌ SSE endpoint: FAILED ({response.status_code})")
                return False
    except Exception as e:
        print(f"   ❌ SSE connection: FAILED ({e})")
        return False

    # Test 2: Health check
    print("\n2. Testing server health...")
    try:
        async with httpx.AsyncClient() as client:
            # The root path should return 404 or redirect, that's ok
            response = await client.get("http://localhost:9001/", timeout=5.0)
            print(f"   ℹ️  Root endpoint: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Root endpoint check: {e}")

    print("\n" + "=" * 50)
    print("MCP Server Test Complete")
    print("=" * 50)
    print("\n✅ Server is running and responding correctly")
    print("If Claude still can't connect, try:")
    print("  1. Restart Claude completely")
    print("  2. Check Claude's MCP configuration")
    print("  3. Verify no firewall is blocking port 9001")
    print("  4. Try reconnecting with /mcp command")

    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_mcp_connection())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        sys.exit(1)