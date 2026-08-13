# TermiChat 🚀

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)
![Vercel](https://img.shields.io/badge/vercel-serverless-black.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

TermiChat is a real-time, cross-platform messaging application featuring zero-dependency Python CLI sockets and a modern, mobile-friendly Web interface.

## Highlights ⚡

- **Dual Operating Modes**: Use terminal CLI sockets (`termichat_server.py` & `termichat_client.py`) or modern Web UI (`index.html`).
- **Hybrid Real-Time Transport**:
  - Automatically connects to local WebSocket server when running locally.
  - Seamlessly fails over to Vercel Serverless API (`/api/messages`) for 5G & mobile CGNAT cloud connectivity.
- **Custom User Handles**: Persistent custom user handles saved in local storage.

## Quickstart Guide 🛠️

### Web & WebSocket Server (Local)
```bash
python3 web_server.py
```
Open `http://localhost:8000` in your web browser.

### Terminal Socket Mode
**Server:**
```bash
python3 termichat_server.py
```
**Client:**
```bash
python3 termichat_client.py
```

## System Architecture 🏗️

```
┌─────────────────────────────────────────────────────────┐
│                      TermiChat                          │
├──────────────────────────┬──────────────────────────────┤
│   Terminal Socket Mode   │       Web Interface Mode     │
│  (termichat_server.py)   │       (index.html UI)        │
│  (termichat_client.py)   │              │               │
└────────────┬─────────────┴──────────────┼───────────────┘
             │                            │
             ▼                            ▼
      Direct TCP Sockets         ┌─────────────────────────┐
         (Port 5555)             │ WebSocket (Local 8000)  │
                                 │        -- OR --         │
                                 │ Vercel Serverless API   │
                                 │   (/api/messages)       │
                                 └─────────────────────────┘
```

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing 🤝

Contributions are welcome! Check out [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

