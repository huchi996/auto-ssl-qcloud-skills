#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auto SSL: issue Let's Encrypt certs via acme.sh and upload to Tencent Cloud SSL.

Usage:
    python auto_ssl.py issue blog.huoyan.cc
    python auto_ssl.py upload blog.huoyan.cc
    python auto_ssl.py issue-and-upload blog.huoyan.cc
    python auto_ssl.py list
"""

import json
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

ACME_SH = Path.home() / ".acme.sh" / "acme.sh"
ACME_DIR = Path.home() / ".acme.sh"

SECRET_ID = os.environ.get("COS_SECRET_ID", "")
SECRET_KEY = os.environ.get("COS_SECRET_KEY", "")
DNS_API = os.environ.get("DNS_API", "dns_tencent")


def run_acme(args: list[str]) -> bool:
    cmd = [str(ACME_SH)] + args
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def issue(domain: str) -> bool:
    """Issue a new certificate via acme.sh DNS validation."""
    cert_dir = ACME_DIR / f"{domain}_ecc"
    if (cert_dir / f"{domain}.cer").exists():
        print(f"Certificate for {domain} already exists, renewing...")
        return run_acme(["--renew", "-d", domain])
    return run_acme(["--issue", "-d", domain, "--dns", DNS_API])


def upload(domain: str) -> str | None:
    """Upload certificate to Tencent Cloud SSL service."""
    if not SECRET_ID or not SECRET_KEY:
        print("Error: COS_SECRET_ID and COS_SECRET_KEY not set in .env")
        sys.exit(1)

    from tencentcloud.common import credential
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile
    from tencentcloud.ssl.v20191205 import models as ssl_models
    from tencentcloud.ssl.v20191205 import ssl_client

    cert_dir = ACME_DIR / f"{domain}_ecc"
    cert_file = cert_dir / f"{domain}.cer"
    key_file = cert_dir / f"{domain}.key"

    if not cert_file.exists() or not key_file.exists():
        print(f"Error: certificate files not found in {cert_dir}")
        return None

    cert = cert_file.read_text()
    key = key_file.read_text()

    cred = credential.Credential(SECRET_ID, SECRET_KEY)
    http = HttpProfile(endpoint="ssl.tencentcloudapi.com")
    client_prof = ClientProfile(httpProfile=http)
    client = ssl_client.SslClient(cred, "", client_prof)

    req = ssl_models.UploadCertificateRequest()
    req.CertificatePublicKey = cert
    req.CertificatePrivateKey = key
    req.Alias = f"{domain}-letsencrypt"
    req.Repeatable = False

    resp = client.UploadCertificate(req)
    cert_id = resp.CertificateId
    repeat = getattr(resp, "RepeatCertificateId", None)
    print(f"Uploaded {domain}. ID: {cert_id} ({'Repeat' if repeat else 'New'})")
    return cert_id


def issue_and_upload(domain: str) -> str | None:
    """Issue (or renew) certificate and upload to Tencent Cloud."""
    if not issue(domain):
        print(f"Failed to issue certificate for {domain}")
        return None
    return upload(domain)


def list_certs():
    """List all locally managed acme.sh certificates."""
    for d in sorted(ACME_DIR.iterdir()):
        if d.is_dir() and d.name.endswith("_ecc"):
            domain = d.name.removesuffix("_ecc")
            cert = d / f"{domain}.cer"
            fullchain = d / "fullchain.cer"
            if cert.exists():
                print(f"  {domain}  ({cert})")
            if fullchain.exists():
                print(f"           ({fullchain})")


COMMANDS = {
    "issue": ("Issue or renew a certificate", issue),
    "upload": ("Upload certificate to Tencent Cloud SSL", upload),
    "issue-and-upload": ("Issue and upload in one step", issue_and_upload),
    "list": ("List local certificates", list_certs),
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"Usage: python {sys.argv[0]} <command> [domain]\n")
        print("Commands:")
        for name, (desc, _) in COMMANDS.items():
            print(f"  {name:20s} {desc}")
        sys.exit(1)

    cmd = sys.argv[1]
    desc, fn = COMMANDS[cmd]

    if cmd == "list":
        fn()
    elif len(sys.argv) < 3:
        print(f"Error: '{cmd}' requires a domain argument")
        sys.exit(1)
    else:
        fn(sys.argv[2])


if __name__ == "__main__":
    main()
