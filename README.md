# auto-ssl-qcloud

Auto SSL certificate management with Let's Encrypt + Tencent Cloud SSL upload.

Automates the full SSL certificate lifecycle:
- **Issue/Renew** certificates via [acme.sh](https://github.com/acmesh-official/acme.sh) with DNS-01 validation (Tencent Cloud DNS)
- **Upload** certificates to Tencent Cloud SSL service

## Prerequisites

- Python 3.10+
- [acme.sh](https://github.com/acmesh-official/acme.sh) installed (`~/.acme.sh/acme.sh`)
- Tencent Cloud account with API credentials

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/huchi996/auto-ssl-qcloud-skills.git
cd auto-ssl-qcloud-skills
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure credentials
cp .env.example .env
# Edit .env, fill in your Tencent Cloud API credentials:
#   COS_SECRET_ID=your_secret_id
#   COS_SECRET_KEY=your_secret_key

# 3. Make sure acme.sh is configured with Tencent Cloud DNS API
export Tencent_SecretId="your_secret_id"
export Tencent_SecretKey="your_secret_key"
```

## Usage

```bash
source .venv/bin/activate

# Issue a new certificate
python auto_ssl.py issue example.com

# Renew an existing certificate (automatic if already issued)
python auto_ssl.py issue example.com

# Upload certificate to Tencent Cloud SSL
python auto_ssl.py upload example.com

# Issue + upload in one step
python auto_ssl.py issue-and-upload example.com

# List all locally managed certificates
python auto_ssl.py list
```

## Claude Code Integration

This project includes a Claude Code skill at `.claude/skills/auto-ssl-qcloud/SKILL.md`. When using Claude Code in this project, Claude can directly help you manage SSL certificates.

## Configuration

Environment variables (set in `.env`):

| Variable | Required | Default | Description |
|---|---|---|---|
| `COS_SECRET_ID` | Yes | - | Tencent Cloud API Secret ID |
| `COS_SECRET_KEY` | Yes | - | Tencent Cloud API Secret Key |
| `DNS_API` | No | `dns_tencent` | DNS provider for acme.sh |

## How It Works

```
acme.sh --issue --dns dns_tencent  -->  ~/.acme.sh/<domain>_ecc/*.cer + *.key
                                              |
                                              v
                                    Tencent Cloud SSL UploadCertificate API
                                              |
                                              v
                                    Certificate available in Tencent Cloud Console
```

## License

MIT
