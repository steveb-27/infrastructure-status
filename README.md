# Infrastructure Status
by Steve B-27
## What IS is
InfrastructureStatus is a Python command-line tool that audits self-managed
infrastructure, regardless of whether services are hosted on-premises, in
the cloud, or across multiple providers. It goes beyond asking a server if
it is up, it asks what it is actually doing. Configuration drifts over time,
and as projects evolve and expand, it can be tough to keep track of. IS uses
self-contained modules for collecting configuration from services such as:
- Cloudflare DNS
- Nginx
- Postfix
- Certbot
- Bunny CDN
- SSL Certificate Configuration

After collecting configuration data, IS validates what has been collected
with modular tests. Rather than simply reporting configuration values,
it compares them against expected infrastructure state and highlights
inconsistencies before they become outages.

- The website might still be online even though a CNAME points nowhere.
- Email might still work even though you're using a self-signed certificate.
- Nginx might still be serving traffic while Cloudflare has stale DNS.
- A CDN might still exist while no hostname is mapped to it.

IS is detecting configuration drift, not just outages.

IS is completely modular, and easily expanded. Use it for verifying
existing architecture, ensuring all systems remain functional after
system upgrades, verify mass configuration changes across the network,
and anything else that can be managed locally, by API, or by SSH.

## What IS Next
IS is under active development. While the current tests are functional,
more work coming down the line include:

**DNS**
- Additional DNS validation
- Automatic identification of third-party providers

**Email**
- SPF validation
- DKIM validation
- DMARC validation
- DKIM provisioning
- Skip email validation for externally hosted domains

**Infrastructure**
- PHP-FPM socket validation
- PHP version consistency
- Twilio phone system validation

**Interface**
- Interactive remediation
- React dashboard

## Why IS it?
I've been hosting websites since the late 1990s. Starting with a FreeBSD
server I built with an old VCR case and 56k modem, my hosting experience 
has evolved into a collection of web servers, mail servers, DNS providers,
CDNs, SSL certificates, and over a dozen domains. Routine operating
system upgrades or configuration changes often required manually verifying
hundreds of settings spread across multiple services.

InfrastructureStatus was created to automate those checks. It serves as a
repeatable infrastructure audit that verifies DNS, web server, email, and
certificate configuration before and after system changes, reducing the
chance of subtle configuration drift causing production issues.

## Installation
```commandline
git clone ...
python -m venv .venv
pip install -r requirements.txt
cp env.example .env
python main.py
```

## Current Features
- Cloudflare DNS collector
- Nginx configuration collector
- Postfix configuration collector
- Certbot certificate collector
- Bunny CDN collector
- Public IP detection
- DNS validation
- Email configuration validation
- SSL certificate validation

## Architecture
```text
Collectors Collect
        │
        ▼
     Context
        │
        ▼
Validators Validate
        │
        ▼
     Results
        │
        ▼
Collectors Remediate
```