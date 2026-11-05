<details>
<summary><strong>FULL DISCLOSURE</strong> — AI Development & Legal Notice</summary>

---

### AI Development Disclosure

This tool is part of the **pr0t31n toolkit**, a collection of security testing and penetration testing automation tools. The toolkit was created through AI-assisted development, guided by the professional experience and domain expertise of a cybersecurity consultant and penetration tester. Ya, I named it after myself - but to be fair, AI is horrible at naming things.

**The pr0t31n toolkit exists to serve two purposes:**

1. **Automate repetitive penetration testing workflow steps.** Security assessments involve significant amounts of repetitive, procedural work — running sequential tool chains, parsing outputs, correlating findings across tools, and managing engagement data. Automating these steps frees testers to focus on the work that requires human judgment: manual testing, creative attack paths, analysis, and reporting.

2. **Demonstrate the benefits and failures of AI-assisted development.** This toolkit is a real-world case study in building production security tooling with AI assistance. It demonstrates both what AI-assisted development can accomplish and where it falls short. The quality of AI-generated code varies significantly — between context refreshes, the output can range from senior/principal-level software engineering to the work of a still-in-school intern. This inconsistency is itself part of the demonstration.

In the interest of transparency, every tool in the pr0t31n toolkit carries this disclosure. The creator believes that AI-assisted development should be acknowledged openly, not concealed. Users, reviewers, and anyone examining this code should know how it was built so they can evaluate it accordingly.

---

### Legal & Authorization Notice

> **⚠ WARNING: AUTHORIZED USE ONLY**

This tool is designed and intended **exclusively** for use in **authorized security testing engagements**. "Authorized" means **all** of the following conditions are met:

- **Explicit Written Permission.** You possess explicit, documented, written authorization from the owner or authorized representative of the target system(s), network(s), or application(s) to conduct security testing. Verbal agreements are not sufficient.
- **Defined Scope.** The authorization clearly defines the scope of testing, including which systems, networks, IP ranges, applications, and/or endpoints are included. You must not exceed the boundaries of this defined scope under any circumstances.
- **Defined Timeframe.** The authorization specifies the dates and times during which testing is permitted. Testing outside the authorized window is unauthorized testing.
- **Rules of Engagement.** You are operating under a set of rules of engagement (RoE) or equivalent governing document that establishes acceptable testing methods, escalation procedures, emergency contacts, and any restrictions or exclusions.
- **Legal Compliance.** Your testing complies with all applicable local, state, national, and international laws and regulations, including but not limited to the Computer Fraud and Abuse Act (CFAA), the General Data Protection Regulation (GDPR), and equivalent legislation in your jurisdiction.

**Prohibited uses** include but are not limited to: unauthorized access to or testing of any system; testing against systems without explicit written authorization; any activity that violates applicable laws; use for malicious purposes including data theft, extortion, sabotage, or disruption of services; distribution intended to facilitate unauthorized access; and use without a clear legal basis.

**THIS TOOL IS PROVIDED "AS IS," WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT.**

The creator(s) and contributor(s) accept no responsibility or liability for any damage, loss, legal consequence, or other harm resulting from the use or misuse of this tool — including damage to systems or data, legal penalties or prosecution, loss of data or revenue, and any direct, indirect, incidental, special, consequential, or punitive damages.

**By using this tool, you acknowledge that you are solely responsible for ensuring that your use is authorized, lawful, and within the defined scope of your engagement. You assume all risk associated with the use of this tool.**

Security testing is a professional discipline with significant ethical and legal obligations. Users operating in a professional capacity are expected to adhere to the standards and codes of conduct established by recognized industry bodies, including PTES, OWASP, NIST, and any certifying body under which they hold credentials.

---

</details>

# Scattershot3

**Automated network penetration testing orchestrator** — host discovery through Active Directory compromise, in a single script.

Scattershot3 takes a list of IPs, ranges, or CIDRs, classifies them as internal or external automatically, and runs a structured multi-phase assessment pipeline: ping sweep, port scanning, banner grabbing, web probing, SSL/TLS analysis, vulnerability scanning, SMB/SNMP/NFS/IPMI enumeration, Responder poisoning, credential brute force, database attacks, AD graph collection, web application DAST, and O365 account enumeration. All results are written to structured JSON/CSV/XLSX output for direct import into reports.

---


> **[View full documentation on the Codex Wiki](https://wiki.pr0t31n.com/tools/scattershot3)** — detailed features, CLI reference, findings catalogue, and integration guides.

## Features

- **Automatic INT/EXT classification** — RFC-1918 addresses go to the internal pass; routable IPs go to external. Each scope gets its own isolated output directory and its own full pipeline run.
- **Multi-phase pipeline** — From ping sweep to O365 enumeration, every phase gates on the results of the previous one (no redundant tool runs against dead hosts).
- **30+ tool integrations** — nmap, rustscan, sslscan, testssl.sh, ssh-audit, Nuclei, gobuster, wpscan, Responder, smbmap, enum4linux, Hydra, BruteSpray, sqlmap, XSStrike, ZAP, BloodHound-Python, Kerbrute, odat, msdat, enumdb, searchsploit, Sploitus, Metasploit (module search), o365spray, webanalyze, shcheck, snmpwalk, and more.
- **Crucible integration** — Set `CRUCIBLE_MANAGED=1` to emit structured protocol tokens for the Crucible web UI. All output streams switch to JSON protocol messages; phases report live status.
- **Scan resumption** — `checkpoint.json` tracks every completed phase and host. Re-running with the same `--project` name skips already-finished work.
- **Credential chaining** — A shared `CredentialStore` passes discovered credentials forward across phases (banner grabs, Hydra, BruteSpray, database attacks, AD tools).
- **Flexible target input** — Inline args, `--targets-file`, JSON settings file, CIDR, hyphen ranges (`192.168.1.1-20`), and individual IPs all work together.
- **Target exclusions** — `--exclude` removes IPs/ranges/CIDRs from the scan after expansion.
- **Rich output** — `findings.json`, `findings.csv`, `findings.xlsx` (multi-sheet, styled), `correlated.json` (IP->port->tool correlation), `software_inventory.json`, and a top-level `summary.json`.
- **Passive seed** — A concurrent tcpdump thread runs alongside Phase 1 discovery, capturing broadcast traffic (SSDP, mDNS, LLMNR, LLDP, ARP). The pcap is handed to Trawler in hunt mode (with the testing server excluded) to discover hosts and services that don't respond to active probes. Discovered IPs and Trawler findings are merged into the scan queue.
- **AI/ML service detection** — Automatically fingerprints AI inference engines (Ollama, vLLM, Triton), ML platforms (MLflow, Ray), UI frameworks (Gradio, Streamlit), and vector databases (Milvus, Qdrant, Chroma) during port scanning. Emits findings and action items for pAIn AI red-team follow-up.
- **Adaptive concurrency** — Port-scan workers auto-scale based on CPU/RAM utilization, bounded to [4, 64] workers.
- **Automatic route setup** — On Linux, adds kernel routes for internal subnets via the detected interface and gateway so probes reach the correct interface on multi-homed hosts. Includes probe-based validation with rollback on failure.
- **CVE correlation** — Correlates software inventory against OSV/NVD databases for known CVEs.
- **Metasploit module search** — Queries the local Metasploit module database for every CVE discovered during the scan.
- **UDP scanning** — Supplementary top-N UDP port scan per host.
- **O365 account enumeration** — Detects Microsoft 365 tenants on external domains and enumerates valid accounts via Azure AD APIs and o365spray.
- **Cross-platform** — Linux, macOS, Windows. Route setup and Responder are Linux-only; all other phases run everywhere.

---

## Scan Phases

| # | Phase | Tools | Condition |
|---|-------|-------|-----------|
| 1 | **Host Discovery** | nmap `-sn`, passive tcpdump seed | Always (passive seed unless `--no-passive-seed`) |
| 1.5 | **Hostname Resolution** | PTR/rDNS, nbtscan, nmblookup, avahi-resolve | Unless `--no-hostname-scan` |
| 1c | **Host Rescue** | rustscan / nmap `-Pn` | Dead hosts from Phase 1 |
| 2 | **Port Scan + Service Probing** | nmap / rustscan, sslscan, testssl.sh, ssh-audit (per SSH port), web probing, banner grab, screenshots, UDP scan | Always on live hosts |
| 2.H | **AI/ML Service Detection** | HTTP fingerprinting (Ollama, Gradio, Streamlit, vLLM, Triton, MLflow, etc.) | AI port or banner detected |
| 3 | **Vulnerability Scanning** | Nuclei (CVE, misconfig, exposed-panels, default-login, network, exposure, auth-bypass) | Unless `--no-nuclei` |
| 4 | **Exploit Lookup** | searchsploit (`--nmap`) | Unless `--no-searchsploit` |
| 4b | **Sploitus** | Sploitus REST API | Always (after Phase 4) |
| 4c | **Metasploit Search** | msfconsole search | Unless `--no-metasploit` |
| 4d | **CVE Correlation** | OSV/NVD lookup against software inventory | Unless `--no-cve-correlation` |
| 5 | **Database Attacks** | odat (Oracle), msdat (MSSQL), enumdb (MySQL/MSSQL) | Ports 1433/1434/1521/3306 open |
| 6 | **Credential Brute Force** | Hydra (SSH, FTP, RDP, SMB, HTTP, VNC, MSSQL, MySQL) | Unless `--no-brute`; applicable services detected |
| 6b | **BruteSpray** | BruteSpray default credential spray | Unless `--no-brute` |
| 7 | **Web Enumeration** | gobuster, wpscan, webanalyze, shcheck | Unless `--no-web` / `--no-gobuster` / `--no-wpscan` / `--no-webanalyze` / `--no-shcheck` |
| 8 | **LLMNR/NBT-NS Poisoning** | Responder | Internal scope, Linux only, unless `--no-responder` |
| 9 | **SMB / RPC Enumeration** | smbmap, enum4linux, ADenum, rpcclient | Unless `--no-enum` |
| 10 | **SNMP Enumeration** | snmpwalk | Unless `--no-snmp` |
| 12 | **Active Directory Assessment** | ldapdomaindump, Kerbrute, BloodHound-Python | Internal scope, DC detected (ports 88/389/3268) |
| 13 | **Web Application DAST** | OWASP ZAP, sqlmap, XSStrike | Web services found |
| 14 | **O365 Account Enumeration** | Azure AD GetCredentialType API, o365spray | External scope; domain has O365 tenant |

---

## CLI Reference

All flags accepted by `scattershot3.py`. CLI arguments always override settings-file values.

### Settings and Setup

| Flag | Short | Type / Default | Description |
|------|-------|----------------|-------------|
| `--settings FILE` | `-s` | str / none | Path to a JSON settings file. Populates engagement metadata (consultant, client, dates) and scan defaults. Run `--init-settings` to generate a template. |
| `--init-settings` | | flag | Write a settings-file template to `scattershot3_settings.json` in the current directory and exit. |

### Targets

| Flag | Short | Type / Default | Description |
|------|-------|----------------|-------------|
| `TARGETS` (positional) | | str / none | IPs, IP ranges (`192.168.1.1-20`), or CIDR blocks. Combinable with `--targets-file` and settings file. |
| `--targets-file FILE` | `-T` | str / none | Newline-separated file of targets (IPs, ranges, CIDRs). Blank lines and `#` comments ignored. Merged with positional targets and settings-file targets. |
| `--exclude SPEC [SPEC ...]` | `-X` | list / `[]` | IPs, IP ranges, or CIDR blocks to EXCLUDE from scanning. Removed after expansion, before any scan pass begins. Also accepted via `scan.exclude` in the settings file. |

### Project

| Flag | Short | Type / Default | Description |
|------|-------|----------------|-------------|
| `--project NAME` | `-p` | str / none | Project directory name. Creates `<name>/internal/` and `<name>/external/` with isolated tool subdirs, logs, and reports. Can also be set via `scan.project` in the settings file. |

### Scan Options

| Flag | Short | Type / Default | Description |
|------|-------|----------------|-------------|
| `--fast` | | flag | Scan top 1000 ports instead of all 65535 ports (faster). |
| `--output FILE` | `-o` | str / none | Also save the combined cross-scope summary to this JSON file. |
| `--port-scan-workers N` | | int / adaptive | Number of hosts to port-scan concurrently. Each worker spawns its own nmap subprocess. Adaptive default based on CPU/RAM (clamped to 4-64). Set to 1 for sequential. |

### Nmap Discovery Tuning

| Flag | Type / Default | Description |
|------|----------------|-------------|
| `--discovery-min-rate N` | int / none | Set nmap `--min-rate` for the `-sn` discovery scan. Controls minimum packet transmission rate (packets/sec). |
| `--discovery-min-parallelism N` | int / none | Set nmap `--min-parallelism` for the `-sn` discovery scan. Controls minimum concurrent probe groups. |
| `--timing-template 0-5` | str / none | Nmap timing template for discovery scans (0=paranoid, 1=sneaky, 2=polite, 3=normal, 4=aggressive, 5=insane). |

### Route Setup (Linux only)

| Flag | Type / Default | Description |
|------|----------------|-------------|
| `--no-route-setup` | flag | Skip automatic internal-route setup. By default, SS3 adds kernel routes for internal target subnets via the detected internal interface and gateway. |
| `--dry-run-routes` | flag | Print the `ip route add` commands that would be executed without actually running them. Route detection still runs. |
| `--route-gateway IP` | str / auto | Explicit next-hop gateway for internal-route setup. Overrides auto-detection. Use when target networks are reachable via a non-default gateway. |
| `--route-interface IFACE` | str / auto | Explicit outbound interface for internal-route setup. Overrides auto-detection. Pair with `--route-gateway`. |
| `--route-validation-threshold FRACTION` | float / `0.33` | Minimum probe-success rate (0.0-1.0) for a candidate (interface, gateway) pair to be accepted. Failure rolls back routes and tries the next candidate. |
| `--route-validation-timeout SECS` | int / `2` | Per-probe ping timeout (seconds) during route validation. |

### Phase Disable Flags

| Flag | Type | Description |
|------|------|-------------|
| `--no-web` | flag | Skip HTTP probing (port fingerprinting only). |
| `--no-banner` | flag | Skip banner grabbing for open ports. |
| `--no-ssl` | flag | Skip SSL/TLS scanning with testssl and sslscan. |
| `--no-nuclei` | flag | Skip Nuclei vulnerability scanning. |
| `--no-hostname-scan` | flag | Skip Phase 1.5 hostname resolution (reverse DNS, nbtscan, nmblookup, avahi-resolve). |
| `--no-enum` | flag | Skip SMB null-session, RPC null-session, FTP anonymous-login, enum4linux, ADenum, and smbmap checks. |
| `--no-snmp` | flag | Skip SNMP community-string checks and snmpwalk. |
| `--no-responder` | flag | Skip Responder (LLMNR/NBT-NS/mDNS poisoner). Linux-only; automatically skipped on macOS and Windows. |
| `--no-screenshots` | flag | Skip Selenium web screenshots. |
| `--no-gobuster` | flag | Skip GoBuster directory enumeration against web services. |
| `--no-wpscan` | flag | Skip WPScan WordPress vulnerability scanning. |
| `--no-webanalyze` | flag | Skip webanalyze technology-stack fingerprinting. |
| `--no-searchsploit` | flag | Skip searchsploit exploit-DB lookup against nmap XML output. |
| `--no-cve-correlation` | flag | Disable OSV/NVD CVE correlation against software inventory. |
| `--no-brute` | flag | Skip Hydra brute force and BruteSpray default credential spray. |
| `--no-shcheck` | flag | Skip shcheck HTTP security header analysis. |
| `--no-passive-seed` | flag | Disable passive-seed tcpdump capture entirely. |
| `--no-udp` | flag | Skip supplementary UDP top-port scan. |
| `--no-metasploit` | flag | Skip Phase 4c Metasploit module search against discovered CVEs. |

### Timeouts

| Flag | Type / Default | Description |
|------|----------------|-------------|
| `--web-timeout SECS` | int / `4` | Timeout in seconds for HTTP probes. |
| `--banner-timeout SECS` | float / `3.0` | Timeout in seconds for banner grab connections. |
| `--sslscan-timeout SECS` | int / `60` | Timeout in seconds for sslscan invocations. |
| `--testssl-timeout SECS` | int / `300` | Timeout in seconds for testssl invocations. testssl runs ~20 checks sequentially and typically needs 90-180s. |
| `--nuclei-timeout SECS` | int / `600` | Timeout in seconds for Nuclei scan. |
| `--gobuster-timeout SECS` | int / `600` | Per-endpoint timeout for GoBuster directory enumeration. |
| `--wpscan-timeout SECS` | int / `300` | Per-site timeout for WPScan. |
| `--searchsploit-timeout SECS` | int / `120` | Per-file timeout for searchsploit `--nmap`. |
| `--brutespray-timeout SECS` | int / `600` | Timeout for BruteSpray credential spray. |
| `--msf-timeout SECS` | int / `60` | Per-CVE timeout for msfconsole search. |

### Tool Paths and Tokens

| Flag | Type / Default | Description |
|------|----------------|-------------|
| `--wpscan-token TOKEN` | str / none | WPScan API token for vulnerability database lookups. Without a token WPScan still runs but vulnerability data is limited. |
| `--msfconsole-path PATH` | str / auto | Path to msfconsole binary (auto-detected when omitted). |

### Protocol and Domain

| Flag | Type / Default | Description |
|------|----------------|-------------|
| `--domain DOMAIN` | str / none | Windows domain hint passed to enum4linux and ADenum when credentials are discovered automatically during the scan. |
| `--email-file FILE` | str / none | File with email addresses (one per line) for O365 account enumeration. If not provided, SS3 looks for OSift output in the project tree. |

### UDP Scanning

| Flag | Type / Default | Description |
|------|----------------|-------------|
| `--udp-top-ports N` | int / `20` | Number of top UDP ports to scan per host in the supplementary UDP pass. Ignored when `--no-udp` is set. |

### Passive Seed

| Flag | Type / Default | Description |
|------|----------------|-------------|
| `--passive-seed-duration SECS` | int / `300` | Duration in seconds for the passive recon tcpdump capture (default: 5 minutes). Runs concurrently with Phase 1 discovery. A longer window catches more broadcast cycles (SSDP ~30-60s, mDNS, LLMNR, ARP). Trawler analyses the pcap in hunt mode with `--ignore` for the testing server. |

### Output Directory Overrides

| Flag | Type / Default | Description |
|------|----------------|-------------|
| `--internal-dir DIR` | str / `<project>/int/` | Override output directory for internal-scope results. |
| `--external-dir DIR` | str / `<project>/ext/` | Override output directory for external-scope results. |

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
| `brutespray` | Optional | Default credential spray |
| `rustscan` | Optional | Fast port discovery (replaces nmap port scan) |
| `kerbrute` | Optional | Kerberos username enumeration |
| `bloodhound-python` | Optional | AD graph collection |
| `sqlmap` | Optional | SQL injection testing |
| `odat` | Optional | Oracle database attacks |
| `msdat` | Optional | MSSQL attacks |
| `enumdb` | Optional | MySQL/MSSQL enumeration |
| `searchsploit` | Optional | Exploit-DB lookup against nmap output |
| `webanalyze` | Optional | Technology-stack fingerprinting |
| `shcheck` | Optional | HTTP security header analysis |
| `snmpwalk` | Optional | SNMP enumeration |
| `msfconsole` | Optional | Metasploit module search for discovered CVEs |
| `o365spray` | Optional | O365 account enumeration |

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

# Exclude lab hosts
python3 scattershot3.py 10.0.0.0/24 --exclude 10.0.0.1 10.0.0.254 --project prod_only

# External scan with O365 enumeration
python3 scattershot3.py 203.0.113.0/28 --email-file emails.txt --project ext_2026

# Preview internal routes without applying them
python3 scattershot3.py 10.10.0.0/24 --project test --dry-run-routes
```

### Settings file
Generate a template and edit it once per engagement:
```bash
python3 scattershot3.py --init-settings
# Edit scattershot3_settings.json with engagement metadata and targets
python3 scattershot3.py --settings scattershot3_settings.json
```

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
    "no_banner":          false,
    "no_web":             false,
    "no_nuclei":          false,
    "no_brute":           false,
    "port_scan_workers":  10,
    "web_timeout":        4,
    "banner_timeout":     3.0,
    "sslscan_timeout":    60,
    "testssl_timeout":    300,
    "nuclei_timeout":     600,
    "brutespray_timeout": 600,
    "wpscan_token":       "YOUR_TOKEN_HERE",
    "discovery_min_rate":        0,
    "discovery_min_parallelism": 20,
    "timing_template":           "",
    "passive_seed_duration":     300,
    "exclude":            []
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
│   ├── ai/                     AI/ML service probe evidence (per host)
│   ├── smb/                    smbmap, enum4linux, rpcclient output
│   ├── snmp/                   snmpwalk output per host
│   ├── responder/              Responder captured hashes
│   ├── bloodhound/             BloodHound-Python zip archives
│   ├── scan.log                human-readable progress log
│   ├── scan.log.json           structured JSON log
│   ├── errors.log              tool errors and exceptions
│   ├── findings.json           <- security findings (primary output)
│   ├── findings.csv            findings in CSV format
│   ├── findings.xlsx           styled multi-sheet Excel workbook
│   ├── correlated.json         IP -> port -> tool correlation map
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

## Crucible Integration

When launched by Crucible (`CRUCIBLE_MANAGED=1`), Scattershot3 switches to structured protocol output:

| Token | Purpose |
|-------|---------|
| `__CRUCIBLE_LOG__:` | Standard log line forwarded to UI console |
| `__CRUCIBLE_ERR__:` | Error line forwarded to UI |
| `__CRUCIBLE_STATUS__:` | Phase progress update |
| `__CRUCIBLE_PROMPT__:` | Interactive prompt requiring user response |
| `__CRUCIBLE_FINDING__:` | Finding emitted in real time |
| `__CRUCIBLE_TARGET__:` | Target/host discovery (including AI service metadata) |
| `__CRUCIBLE_PORT__:` | Port discovery |
| `__CRUCIBLE_ACTION_ITEM__:` | Action item (e.g., pAIn follow-up recommendation) |

Dependency installs are non-interactive (auto-approved). Phase status is reported live so the Crucible UI can track progress across the pipeline in real time.

---

## AI/ML Service Detection

Phase 2.H runs automatically during port scanning. When a port matches a known AI service port or when HTTP/banner probing reveals AI service indicators, Scattershot3 fingerprints the service by probing known API endpoints.

### Detected services

| Service | Default Port | Probe Endpoint | Type |
|---------|-------------|----------------|------|
| Ollama | 11434 | `/api/tags` | LLM Inference |
| Gradio | 7860 | `/api/version` | ML UI Framework |
| Streamlit | 8501 | `/_stcore/health` | ML UI Framework |
| MLflow | 5000 | `/api/2.0/mlflow/version` | ML Platform |
| vLLM | 8000 | `/v1/models` | LLM Inference |
| NVIDIA Triton | 8001/8002 | `/v2/models/stats` | Model Serving |
| Dify | 3000 | `/api/version` | AI Platform |
| Weaviate | 8080 | `/v1/.well-known/ready` | Vector DB |
| LangFlow | 7681 | `/health` | AI Orchestration |
| Milvus | 19530 | `/v1/vector/collections` | Vector DB |
| Qdrant | 6333/6334 | `/collections` | Vector DB |
| Jupyter | 8888 | `/api/status` | Notebook Server |
| Ray Dashboard | 8265 | `/api/version` | ML Orchestration |
| LiteLLM | 4000 | `/v1/models` | LLM Proxy |
| LocalAI | 5001 | `/v1/models` | LLM Inference |
| ComfyUI | 8188 | `/system_stats` | Image Generation |
| ChromaDB | 7000 | `/api/v1/heartbeat` | Vector DB |

### Findings emitted

| ID | Title | Risk | Condition |
|----|-------|------|-----------|
| SS-AI-001 | AI/ML Service Exposed | MEDIUM | Any AI service reachable |
| SS-AI-002 | AI Service Unauthenticated Access | HIGH | API responds without auth |
| SS-AI-003 | AI Model Inventory Disclosed | MEDIUM | Model list retrievable |
| SS-AI-004 | AI Service Version Disclosed | LOW | Version info leaked |
| SS-AI-005 | Non-Standard AI Service Port | INFO | AI on unexpected port |

When running under Crucible, AI service discoveries emit `__CRUCIBLE_TARGET__` tokens with `ai_service` metadata and `__CRUCIBLE_ACTION_ITEM__` tokens recommending pAIn for AI red-team follow-up.

Evidence files are saved to `hosts/<ip>/ai/` within the scope output directory.

---

## Notes

- **Responder** requires root and a Linux network interface. It is automatically skipped on macOS and Windows.
- **rustscan** is used for port discovery when available; nmap `-sV` is always run on discovered ports for service detection regardless.
- **Phase 12 (AD Assessment)** only runs on the internal scope when ports 88, 389, or 3268 are detected (domain controller indicators).
- **Phase 13 (DAST)** runs OWASP ZAP on port 8091 to avoid conflicts with common web services on 8080.
- **Phase 14 (O365 Enumeration)** runs on the external scope only when a domain has a detected Microsoft 365 tenant. Uses Azure AD GetCredentialType API with o365spray as a fallback.
- All tool timeouts are configurable via CLI flags or the settings file. Long-running tools (testssl, ZAP, BloodHound) default to 300-600 seconds.
- The `--dry-run-routes` flag can be used on Linux to preview internal route additions without executing them.
- **Adaptive concurrency** adjusts `--port-scan-workers` at runtime based on CPU and memory pressure, scaling down under load and back up when resources are available.

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
| responder | Laurent Gaffie | @lgandx | https://github.com/lgandx/Responder |
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
