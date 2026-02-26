# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please email **contact@videodb.io** with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact

We will respond within 48 hours.

---

## Dependencies

All dependencies are pinned to secure version ranges:

- **videodb[capture]** `>=0.4.0` - Core SDK
- **python-dotenv** `>=1.0.0,<2.0.0` - Environment variables
- **requests** `>=2.32.3,<3.0.0` - HTTP client (CVE-2024-35195 patched)
- **flask** `>=3.1.0,<4.0.0` - Web server (optional, capture backend only)
- **pycloudflared** `>=0.2.0,<1.0.0` - Webhook tunnels (optional, capture backend only)

---

## pycloudflared Note

Used only in `scripts/backend.py` for webhook tunneling during real-time capture.

**Security considerations:**
- Downloads official cloudflared binary from Cloudflare
- Optional - only needed for capture features
- For production: use ngrok, localtunnel, or your own reverse proxy

---

## API Key Security

- Store `VIDEO_DB_API_KEY` in environment variables
- Never commit `.env` files
- Get keys from: https://console.videodb.io

---

## Best Practices

1. Use virtual environments for isolation
2. Keep dependencies updated: `pip list --outdated`
3. Review changes for security implications
