# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Single-file Python CLI (`auto_ssl.py`) that automates SSL certificate management:
- Issues/renews Let's Encrypt certs via **acme.sh** (DNS-01 validation with Tencent Cloud DNS)
- Uploads certs to **Tencent Cloud SSL** service via their Python SDK

## Setup & Usage

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in Tencent Cloud credentials

python auto_ssl.py issue <domain>            # issue/renew cert
python auto_ssl.py upload <domain>           # upload to Tencent Cloud SSL
python auto_ssl.py issue-and-upload <domain> # both
python auto_ssl.py list                      # list managed certs
```

No build step, no tests, no linter.

## Architecture

```
main() → COMMANDS dispatch → issue() / upload() / issue_and_upload() / list_certs()
                ↓                        ↓
         run_acme() → acme.sh subprocess  tencentcloud-sdk-python → SSL API
```

- `run_acme()`: subprocess wrapper for `~/.acme.sh/acme.sh`
- `issue()`: calls `acme.sh --issue` or `--renew` with `--dns dns_tencent`
- `upload()`: reads cert files from `~/.acme.sh/<domain>_ecc/`, uploads via Tencent Cloud SSL `UploadCertificate` API
- `list_certs()`: scans `~/.acme.sh/` for `*_ecc` directories

**Dependencies**: `acme.sh` must be installed at `~/.acme.sh/acme.sh`. Cert files live in `~/.acme.sh/<domain>_ecc/`.

## Configuration

Loaded from `.env` via `python-dotenv`:
- `COS_SECRET_ID` / `COS_SECRET_KEY` — Tencent Cloud API credentials
- `DNS_API` — DNS provider for acme.sh (defaults to `dns_tencent`)
