# HTML Email Fix - Technical Documentation

## Problem Statement

The MCP server's `gmail_send_email` tool was not sending HTML emails correctly. When `html=true` was set, emails arrived as plain text instead of rendered HTML.

## Root Cause

The implementation used `--body-file` flag to pass HTML content:

```python
# WRONG: --body-file sends as plain text
args.extend(["--body", "Plain text fallback", "--body-file", html_file])
```

According to gogcli's behavior, `--body-file` reads the file and sends it as plain text, not as HTML.

## Solution

After extensive testing with multiple methods, the **confirmed working solution** is:

### Method: Variable Shell Expansion (Prueba 6)

```python
def run_gogcli_with_expect(
    service: str,
    command: str,
    args: list[str],
    account: str | None = None,
    html_body: str | None = None,
    timeout: int = 60
) -> dict[str, Any]:
    # Create temp file with HTML
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        escaped_html = html_body.replace('\\', '\\\\').replace('"', '\\"')
        f.write(escaped_html)
        html_file = f.name

    # Use expect with variable shell expansion
    expect_script = f'''set timeout {timeout}
set html_body [exec cat {html_file}]
spawn sh -c "gogcli gmail send ... --body-html=$html_body"
expect {{
    "Enter passphrase" {{ send "\\r"; exp_continue }}
    timeout {{ puts "Timeout"; exit 1 }}
    eof
}}
exec rm {html_file}
'''
```

## Test Results

| Method | Result | Message ID |
|--------|--------|------------|
| Variable shell expansion | ✅ WORKS | `19c4434e4fb9417f` |
| Backticks direct | ❌ Text literal | `19c4434fae380f4f` |
| Heredoc double quotes | ❌ Text literal | `19c443528e013be8` |

## Key Requirements

1. **No quotes in HTML attributes**: `style=color:blue` NOT `style="color: blue"`
2. **Single line HTML**: Avoid newlines in HTML content
3. **Use expect with variable**: `set html_body [exec cat file]` then `--body-html=$html_body`

## Usage Example

```json
{
  "tool": "gmail_send_email",
  "arguments": {
    "to": "recipient@example.com",
    "subject": "HTML Email",
    "body": "<h1>Hello</h1><p style=color:blue>Blue text</p>",
    "html": true
  }
}
```

## References

- Confirmed working Message ID: `19c4434e4fb9417f`
- Test date: 2026-02-09
- gogcli version: v0.9.0 (99d9575)