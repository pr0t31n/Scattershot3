# Scattershot3

**Automated network penetration testing orchestrator** — host discovery through Active Directory compromise, in a single script.

Scattershot3 takes a list of IPs, ranges, or CIDRs, classifies them as internal or external automatically, and runs a structured 13-phase assessment pipeline: ping sweep, port scanning, banner grabbing, web probing, SSL/TLS analysis, vulnerability scanning, SMB/SNMP/NFS/IPMI enumeration, Responder poisoning, credential brute force, database attacks, AD graph collection, and full web application DAST. All results are written to structured JSON/CSV/XLSX output for direct import into reports.

---

## Features

- **Automatic INT/EXT classification** — RFC-1918 addresses go to the internal pass; routable IPs go to external. Each scope gets its own isolated output directory and its own full pipeline run.
- **13-phase pipeline** — From ping sweep to OWASP ZAP DAST, every phase gates on the results of the previous one (no redundant tool runs against dead hosts).
- **30+ tool integrations** — nmap, rustscan, sslscan, testssl.sh, ssh-audit, Nuclei, gobuster, wpscan, Responder, smbmap, enum4linux, Hydra, sqlmap, XSStrike, ZAP, BloodHound-Python, Kerbrute, odat, msdat, enumdb, Sploitus, and more.
- **Vantage integration** — Set `VANTAGE_MANAGED=1` to emit structured protocol tokens for the [Vantage](../vantage/) web UI. All output streams switch to JSON protocol messages; phases report live status.
- **Scan resumption** — `checkpoint.json` tracks every completed phase and host. Re-running with the same `--project` name skips already-finished work.
- **Credential chaining** — A shared `CredentialStore` passes discovered credentials forward across phases (banner grabs → Hydra → database attacks → AD tools).
- **Flexible target input** — Inline args, `--targets-file`, JSON settings file, CIDR, hyphen ranges (`192.168.1.1-20`), and individual IPs all work together.
- **Rich output** — `findings.json`, `findings.csv`, `findings.xlsx` (multi-sheet, styled), `correlated.json` (IP→port→tool correlation), `software_inventory.json`, and a top-level `summary.json`.
- **Passive seed** — A concurrent tcpdump thread runs alongside Phase 1 discovery, capturing broadcast traffic (SSDP, mDNS, LLMNR, LLDP, ARP). The pcap is handed to Trawler in hunt mode (with the testing server excluded) to discover hosts and services that don't respond to active probes. Discovered IPs and Trawler findings are merged into the scan queue.
- **Cross-platform** — Linux, macOS, Windows. Route setup and Responder are Linux-only; all other phases run everywhere.

---

## Scan Phases

| # | Phase | Tools | Condition |
|---|-------|-------|-----------|
| 1 | **Host Discovery** | nmap `-sn` | Always |
| 1.5 | **Hostname Resolution** | PTR/rDNS, nbtscan, nmblookup, avahi-resolve | Unless `--no-hostname-scan` |
| 2 | **Port Scan + Service Probing** | nmap / rustscan → sslscan, testssl.sh, ssh-audit (per SSH port), web probing, banner grab, screenshots | Always on live hosts |
| 3 | **Vulnerability Scanning** | Nuclei (CVE, misconfig, exposed-panels, default-login, network, exposure, auth-bypass) | Unless `--no-nuclei` |
| 4 | **Exploit Lookup** | searchsploit (`--nmap`), Sploitus REST API | Unless `--no-searchsploit` |
| 5 | **Database Attacks** | odat (Oracle), msdat (MSSQL), enumdb (MySQL/MSSQL) | Ports 1433/1434/1521/3306 open |
| 6 | **Credential Brute Force** | Hydra (SSH, FTP, RDP, SMB, HTTP, VNC, MSSQL, MySQL) | Applicable services detected |
| 7 | **Web Enumeration** | gobuster, wpscan, webanalyze, shcheck | Unless `--no-web` / `--no-gobuster` |
| 8 | **LLMNR/NBT-NS Poisoning** | Responder | Internal scope, Linux only, unless `--no-responder` |
| 9 | **SMB / RPC Enumeration** | smbmap, enum4linux, ADenum, rpcclient | Unless `--no-enum` |
| 10 | **SNMP Enumeration** | snmpwalk | Unless `--no-snmp` |
| 12 | **Active Directory Assessment** | ldapdomaindump, Kerbrute, BloodHound-Python | Internal scope, DC detected (ports 88/389/3268) |
| 13 | **Web Application DAST** | OWASP ZAP, sqlmap, XSStrike | Web services found |

---

## Requirements

### Python
- Python 3.10+
- `python-nmap`, `colorama`, `requests` (required; auto-installed on first run)
- `selenium`, `openpyxl` (optional; auto-installed on prompt)

### External tools

The following tools must be on `PATH` or discoverable. Missing tools are skipped gracefully with a warning.

| Tool | Required | Purpose |
|------|----------|---------|
| `nmap` | Yes | Host discovery and port scanning |
| `sslscan` | Recommended | SSL/TLS cipher and certificate analysis |
| `testssl` / `testssl.sh` | Recommended | Comprehensive TLS testing |
| `ssh-audit` | Recommended | Deep SSH algorithm + CVE assessment per port |
| `nuclei` | Recommended | Vulnerability scanning |
| `gobuster` | Optional | Directory enumeration |
| `wpscan` | Optional | WordPress vulnerability scanning |
| `responder` | Optional | LLMNR/NBT-NS poisoning (Linux) |
| `smbmap` | Optional | SMB share enumeration |
| `enum4linux` | Optional | SMB/CIFS enumeration |
| `hydra` | Optional | Credential brute force |
| `rustscan` | Optional | Fast port discovery (replaces nmap port scan) |
| `kerbrute` | Optional | Kerberos username enumeration |
| `bloodhound-python` | Optional | AD graph collection |
| `sqlmap` | Optional | SQL injection testing |
| `odat` | Optional | Oracle database attacks |
| `msdat` | Optional | MSSQL attacks |
| `enumdb` | Optional | MySQL/MSSQL enumeration |

**On Kali Linux**, most tools are available via `apt`:
```bash
sudo apt install nmap sslscan testssl.sh ssh-audit nuclei gobuster wpscan responder smbmap enum4linux hydra
```

---

## Installation

Run the included installer once. Scattershot3 itself does NOT install anything
at runtime — it only warns and degrades when tools or Python packages are
missing.

```bash
git clone https://github.com/yourorg/scattershot3
cd scattershot3
sudo python3 install.py        # installs apt / brew / pip / go dependencies
python3 scattershot3.py 192.168.1.0/24 --project corp_internal
```

You can also install/repair Scattershot3 via the Arsenal tool registry.

If you skip install.py and try to run scattershot3.py with required Python
packages missing, it will print a clear list of what's missing and exit
without attempting to fix anything. Optional tools (nuclei, selenium,
ssh-audit, sslscan, testssl, vulners.nse) are reported as warnings; the scan
continues and skips the affected phases.

Missing Python dependencies are detected at startup and offered for auto-install.

---

## Usage

### Quick start
```bash
# Scan a subnet — auto-classifies as internal
python3 scattershot3.py 192.168.10.0/24 --project client_2026

# Mixed internal + external, from a file
python3 scattershot3.py --targets-file targets.txt --project pentest_q1

# Fast scan (top 1000 ports, no screenshots, no DAST)
python3 scattershot3.py 10.0.0.0/16 --project quick --fast --no-screenshots
```

### Settings file
Generate a template and edit it once per engagement:
```bash
python3 scattershot3.py --init-settings
# Edit scattershot3_settings.json with engagement metadata and targets
python3 scattershot3.py --settings scattershot3_settings.json
```

### Common flags

| Flag | Description |
|------|-------------|
| `--project NAME` | Output directory name (default: `scan_output`) |
| `--fast` | Top 1000 ports only |
| `--no-ssl` | Skip sslscan + testssl |
| `--no-web` | Skip HTTP probing and web tools |
| `--no-nuclei` | Skip Nuclei |
| `--no-enum` | Skip SMB/RPC enumeration |
| `--no-snmp` | Skip SNMP enumeration |
| `--no-responder` | Skip Responder |
| `--no-screenshots` | Skip Selenium screenshots |
| `--no-gobuster` | Skip gobuster directory enumeration |
| `--no-wpscan` | Skip WPScan |
| `--port-scan-workers N` | Concurrent host scanners (default: 10) |
| `--domain DOMAIN` | Windows domain hint for AD tools |
| `--wpscan-token TOKEN` | WPScan API token |
| `--targets-file FILE` | Newline-separated targets file (`#` comments supported) |
| `--passive-seed-duration N` | Seconds of concurrent tcpdump capture for Trawler passive analysis (default: 300, 0 = disabled) |
| `--no-passive-seed` | Disable the passive seed capture entirely |

---

## Settings File

The settings file (`--settings`) allows engagement metadata and scan defaults to be persisted across runs without repeating long command lines.

```json
{
  "engagement": {
    "consultant":       "Jane Smith",
    "consultant_email": "jsmith@firm.example",
    "client_name":      "Acme Corporation",
    "client_short":     "acme",
    "client_POC":       "Bob Johnson",
    "client_email":     "bjohnson@acme.example",
    "start_date":       "2026-04-07",
    "end_date":         "2026-04-11"
  },
  "scan": {
    "project":            "acme_2026",
    "targets":            ["10.10.0.0/24", "10.10.1.0/24", "203.0.113.0/28"],
    "target_file":        "",
    "fast":               false,
    "no_ssl":             false,
    "no_nuclei":          false,
    "no_responder":       false,
    "port_scan_workers":  10,
    "wpscan_token":       "YOUR_TOKEN_HERE",
    "passive_seed_duration": 300
  }
}
```

CLI arguments always override settings file values. Generate a full template with `--init-settings`.

---

## Output Structure

```
<project>/
├── internal/
│   ├── nmap/                   nmap XML, grep, and plain-text output
│   ├── sslscan/                sslscan raw output per host
│   ├── testssl/                testssl JSON + text per host
│   ├── nuclei/                 Nuclei findings JSON/CSV
│   ├── banners/                per-port banner capture files
│   ├── web/                    HTTP response bodies + screenshots
│   ├── smb/                    smbmap, enum4linux, rpcclient output
│   ├── snmp/                   snmpwalk output per host
│   ├── responder/              Responder captured hashes
│   ├── bloodhound/             BloodHound-Python zip archives
│   ├── scan.log                human-readable progress log
│   ├── scan.log.json           structured JSON log
│   ├── errors.log              tool errors and exceptions
│   ├── findings.json           ← security findings (primary output)
│   ├── findings.csv            findings in CSV format
│   ├── findings.xlsx           styled multi-sheet Excel workbook
│   ├── correlated.json         IP → port → tool correlation map
│   ├── software_inventory.json detected software and versions
│   └── checkpoint.json         scan resumption state
├── external/                   same structure as internal/
└── summary.json                combined cross-scope findings summary
```

### findings.json schema

```json
[
  {
    "title":     "TLS 1.0 Enabled",
    "severity":  "MEDIUM",
    "type":      "ssl",
    "host":      "192.168.1.50",
    "port":      443,
    "hostname":  "app.internal.corp",
    "tool":      "sslscan",
    "evidence":  "TLSv1  Enabled",
    "cves":      [],
    "scope":     "int",
    "ts":        "2026-04-07T09:14:22"
  }
]
```

Severity values: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`

---

## Vantage Integration

When launched by [Vantage](../vantage/) (`VANTAGE_MANAGED=1`), Scattershot3 switches to structured protocol output:

| Token | Purpose |
|-------|---------|
| `__VANTAGE_LOG__:` | Standard log line forwarded to UI console |
| `__VANTAGE_ERR__:` | Error line forwarded to UI |
| `__VANTAGE_STATUS__:` | Phase progress update |
| `__VANTAGE_PROMPT__:` | Interactive prompt requiring user response |

Dependency installs are non-interactive (auto-approved). Phase status is reported live so the Vantage UI can track progress across the 13-phase pipeline in real time.

---

## Notes

- **Responder** requires root and a Linux network interface. It is automatically skipped on macOS and Windows.
- **rustscan** is used for port discovery when available; nmap `-sV` is always run on discovered ports for service detection regardless.
- **Phase 12 (AD Assessment)** only runs on the internal scope when ports 88, 389, or 3268 are detected (domain controller indicators).
- **Phase 13 (DAST)** runs OWASP ZAP on port 8091 to avoid conflicts with common web services on 8080.
- All tool timeouts are configurable via CLI flags or the settings file. Long-running tools (testssl, ZAP, BloodHound) default to 300–600 seconds.
- The `--dry-run-routes` flag can be used on Linux to preview internal route additions without executing them.

---

## Contributors

Scattershot3 integrates the following external tools and Python libraries. Credits and links are provided for each.

### External Tools

| Tool | Creator | Handle | Link |
|------|---------|--------|------|
| nmap | Gordon Lyon | @Fyodor | https://nmap.org / https://github.com/nmap/nmap |
| masscan | Robert Graham | @robertdavidgraham | https://github.com/robertdavidgraham/masscan |
| nuclei | ProjectDiscovery | @projectdiscovery | https://github.com/projectdiscovery/nuclei |
| httpx | ProjectDiscovery | @projectdiscovery | https://github.com/projectdiscovery/httpx |
| sslscan | rbsec | — | https://github.com/rbsec/sslscan |
| testssl.sh | Dirk Wetter | @dirkw | https://github.com/drwetter/testssl.sh |
| nikto | Chris Sullo | @sullo | https://github.com/sullo/nikto |
| gobuster | OJ Reeves | @TheColonial | https://github.com/OJ/gobuster |
| wpscan | WPScan team | @wpscanteam | https://github.com/wpscanteam/wpscan |
| hydra | van Hauser | @vanhauser-thc | https://github.com/vanhauser-thc/thc-hydra |
| enum4linux | Mark Lowe | @CiscoCXSecurity | https://github.com/CiscoCXSecurity/enum4linux |
| responder | Laurent Gaffié | @lgandx | https://github.com/lgandx/Responder |
| smbmap | ShawnDEvans | — | https://github.com/ShawnDEvans/smbmap |
| BloodHound-Python | Fox-IT | — | https://github.com/fox-it/BloodHound.py |
| Kerbrute | ropnop | — | https://github.com/ropnop/kerbrute |
| sqlmap | sqlmap dev team | — | https://github.com/sqlmapproject/sqlmap |
| XSStrike | s0md3v | — | https://github.com/s0md3v/XSStrike |
| OWASP ZAP | OWASP foundation | — | https://github.com/zaproxy/zaproxy |
| rustscan | RustScan contributors | — | https://github.com/RustScan/RustScan |
| shcheck | santoru | — | https://github.com/santoru/shcheck |
| ADenum | SecuProject | — | https://github.com/SecuProject/ADenum |
| odat | quentinhardy | — | https://github.com/quentinhardy/odat |
| msdat | quentinhardy | — | https://github.com/quentinhardy/msdat |
| searchsploit | Exploit-DB | — | https://github.com/offensive-security/exploitdb |
| webanalyze | rverton | — | https://github.com/rverton/webanalyze |
| Sploitus API | sploitus.com | — | https://sploitus.com |

### Python Libraries

| Library | Creator | Handle | Link |
|---------|---------|--------|------|
| python-nmap | python-nmap contributors | — | https://bitbucket.org/xael/python-nmap |
| scapy | Philippe Biondi | @p-biondi | https://github.com/secdev/scapy |
| requests | PSF / Kenneth Reitz | @kennethreitz | https://github.com/psf/requests |
| netaddr | David P. D. Moss | — | https://github.com/netaddr/netaddr |
| dnspython | Bob Halley | — | https://github.com/rthalley/dnspython |
| colorama | Jonathan Hartley | @tartley | https://github.com/tartley/colorama |
| tqdm | tqdm contributors | — | https://github.com/tqdm/tqdm |
| jinja2 | Pallets project | @mitsuhiko | https://github.com/pallets/jinja |
| ldap3 | Giovanni Cannata | — | https://github.com/cannatag/ldap3 |
| pysnmp | Ilya Etingof | — | https://github.com/etingof/pysnmp |
| impacket | SecureAuth | @SecureAuth | https://github.com/SecureAuthCorp/impacket |
| cryptography | PyCA contributors | — | https://github.com/pyca/cryptography |
| paramiko | Jeff Forcier | @bitprophet | https://github.com/paramiko/paramiko |
| openpyxl | openpyxl contributors | — | https://github.com/theorchard/openpyxl |
