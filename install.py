#!/usr/bin/env python3
"""
Scattershot3 — Network Penetration Testing Orchestrator
Install script
Location: /opt/pr0t31n/Scattershot3/
Symlinks: scattershot3 → scattershot3.py, ss3 → scattershot3.py
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import urllib.request

# ---------------------------------------------------------------------------
# ANSI colours
# ---------------------------------------------------------------------------
R  = "\033[1;31m"
G  = "\033[1;32m"
Y  = "\033[1;33m"
B  = "\033[1;34m"
C  = "\033[1;36m"
W  = "\033[0m"

def banner(msg):  print(f"\n{B}{'='*60}{W}\n{C}  {msg}{W}\n{B}{'='*60}{W}")
def info(msg):    print(f"{G}[+]{W} {msg}")
def warn(msg):    print(f"{Y}[!]{W} {msg}")
def note(msg):    print(f"{Y}[i]{W} {msg}")
def error(msg):   print(f"{R}[x]{W} {msg}")
def step(msg):    print(f"{B}[>]{W} {msg}")

# ---------------------------------------------------------------------------
# OS detection
# ---------------------------------------------------------------------------
def detect_os():
    system = platform.system()
    if system == "Darwin":
        return "macos"
    if system == "Windows":
        return "windows"
    try:
        with open("/etc/os-release") as f:
            data = f.read().lower()
    except FileNotFoundError:
        return "linux-unknown"
    if "kali" in data or "debian" in data or "ubuntu" in data:
        return "apt"
    if "rhel" in data or "centos" in data or "rocky" in data or "fedora" in data:
        return "dnf"
    if "suse" in data or "opensuse" in data:
        return "zypper"
    return "linux-unknown"

OS = detect_os()

# ---------------------------------------------------------------------------
# Privilege helpers
# ---------------------------------------------------------------------------
def is_root():
    return os.getuid() == 0 if hasattr(os, "getuid") else False

def get_sudo_user():
    return os.environ.get("SUDO_USER", "")

# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
def run(cmd, check=True, capture=False, env=None):
    step(" ".join(cmd) if isinstance(cmd, list) else cmd)
    kwargs = dict(check=check)
    if capture:
        kwargs["capture_output"] = True
        kwargs["text"] = True
    if env:
        kwargs["env"] = env
    return subprocess.run(cmd, **kwargs)


def _pip_installed(pkg_spec):
    import importlib.util
    name = pkg_spec.split(">=")[0].split("==")[0].split("[")[0].split("<")[0].strip()
    _IMPORT_MAP = {
        "python-nmap": "nmap", "dnspython": "dns", "pysnmp": "pysnmp",
        "webdriver-manager": "webdriver_manager", "ssh-audit": "ssh_audit",
        "beautifulsoup4": "bs4", "pyyaml": "yaml", "Pillow": "PIL",
        "python-whois": "whois", "pyOpenSSL": "OpenSSL",
        "charset-normalizer": "charset_normalizer",
    }
    mod = _IMPORT_MAP.get(name, name.replace("-", "_"))
    try:
        return importlib.util.find_spec(mod) is not None
    except (ModuleNotFoundError, ValueError):
        return False


# ---------------------------------------------------------------------------
# brew helper — NEVER run as root
# ---------------------------------------------------------------------------
def brew_install(pkg, cask=False):
    brew_path = shutil.which("brew")
    if not brew_path:
        for p in ["/opt/homebrew/bin/brew", "/usr/local/bin/brew"]:
            if os.path.isfile(p):
                brew_path = p
                break
    if not brew_path:
        note(f"brew not found — skipping {pkg}")
        return

    cmd = [brew_path, "install"]
    if cask:
        cmd.append("--cask")
    cmd.append(pkg)
    if is_root():
        sudo_user = get_sudo_user()
        if not sudo_user:
            note(f"Running as root with no SUDO_USER — cannot run brew safely. Skipping {pkg}.")
            return
        cmd = ["sudo", "-u", sudo_user] + cmd

    run(cmd, check=False)

# ---------------------------------------------------------------------------
# Package managers
# ---------------------------------------------------------------------------
_apt_updated = False

def apt_install(packages):
    global _apt_updated
    if not _apt_updated:
        info("Running apt update + apt upgrade …")
        run(["apt-get", "update", "-y"])
        run(["apt-get", "upgrade", "-y"])
        _apt_updated = True
    run(["apt-get", "install", "-y"] + packages)

def dnf_install(packages):
    run(["dnf", "install", "-y"] + packages)

def zypper_install(packages):
    run(["zypper", "install", "-y"] + packages)

# ---------------------------------------------------------------------------
# System packages
# ---------------------------------------------------------------------------
APT_PACKAGES = [
    "nmap", "sslscan", "wpscan",
    "enum4linux", "enum4linux-ng",
    "samba-common-bin", "smbclient", "smbmap",
    "snmp", "snmp-mibs-downloader",
    "nfs-common", "ipmitool",
    "nbtscan", "avahi-utils", "dnsutils",
    "hydra", "exploitdb", "sqlmap",
    "ssh-audit", "ike-scan", "ntpsec",
    # OWASP ZAP for the web-DAST phase
    "zaproxy",
    # Headless browser + driver for the screenshot phase
    "chromium", "chromium-driver",
    "python3-pip", "python3-dev",
    "git", "golang-go",
    "libsasl2-dev", "libldap2-dev", "libkrb5-dev", "libssl-dev",
]
DNF_PACKAGES = [
    "nmap", "sslscan",
    "samba-common-tools", "samba-client", "smbmap",
    "net-snmp-utils",
    "nfs-utils", "ipmitool",
    "avahi-tools", "bind-utils",
    "hydra", "sqlmap", "exploitdb",
    "ssh-audit", "ike-scan",
    # OWASP ZAP and Chromium for screenshots
    "zaproxy", "chromium", "chromedriver",
    "python3-pip", "python3-devel",
    "git", "golang",
    "openssl-devel", "cyrus-sasl-devel", "openldap-devel", "krb5-devel",
    "epel-release",
]
ZYPPER_PACKAGES = [
    "nmap", "sslscan",
    "samba", "samba-client",
    "net-snmp",
    "nfs-client", "ipmitool",
    "avahi", "bind-utils",
    "sqlmap", "ike-scan",
    "chromium", "chromedriver",
    "python3-pip", "python3-devel",
    "git", "golang",
    "openssl-devel",
]
BREW_PACKAGES = [
    "nmap", "sslscan", "hydra", "sqlmap",
    "snmp", "git", "ipmitool", "samba",
    "ssh-audit", "ike-scan", "exploitdb",
    "testssl",
    "rustscan",
    "go",
]
BREW_CASK_PACKAGES = [
    "owasp-zap",
    "chromedriver",
    "metasploit",
]

def install_nbtscan_from_source():
    """Build nbtscan from source on macOS (no Homebrew formula)."""
    if shutil.which("nbtscan"):
        info("nbtscan already installed.")
        return
    import tempfile
    url = "https://github.com/charlesroelli/nbtscan/archive/refs/heads/master.tar.gz"
    info("nbtscan not in Homebrew — building from source …")
    with tempfile.TemporaryDirectory() as td:
        tarball = os.path.join(td, "nbtscan.tar.gz")
        try:
            urllib.request.urlretrieve(url, tarball)
        except Exception as e:
            warn(f"nbtscan download failed: {e}")
            return
        import tarfile
        try:
            with tarfile.open(tarball) as tf:
                tf.extractall(td)
        except Exception as e:
            warn(f"nbtscan extract failed: {e}")
            return
        src = None
        for d in os.listdir(td):
            p = os.path.join(td, d)
            if os.path.isdir(p) and "nbtscan" in d.lower():
                src = p
                break
        if not src:
            warn("nbtscan source directory not found after extraction.")
            return
        try:
            run(["make", "-C", src], check=False)
            binary = os.path.join(src, "nbtscan")
            if os.path.isfile(binary):
                shutil.copy2(binary, "/usr/local/bin/nbtscan")
                os.chmod("/usr/local/bin/nbtscan", 0o755)
                info("nbtscan installed to /usr/local/bin/nbtscan")
            else:
                warn("nbtscan binary not produced by make.")
        except Exception as e:
            warn(f"nbtscan build failed: {e}")


def install_system():
    banner("Phase: system packages")
    if OS == "apt":
        apt_install(APT_PACKAGES)
    elif OS == "dnf":
        dnf_install(DNF_PACKAGES)
    elif OS == "zypper":
        zypper_install(ZYPPER_PACKAGES)
    elif OS == "macos":
        for pkg in BREW_PACKAGES:
            brew_install(pkg)
        for pkg in BREW_CASK_PACKAGES:
            brew_install(pkg, cask=True)
        brew_install("wpscanteam/tap/wpscan")
        install_nbtscan_from_source()
    elif OS == "windows":
        note("Windows: system package installation not supported. Install tools manually.")
    else:
        note(f"Unknown OS '{OS}' — skipping system packages.")

# ---------------------------------------------------------------------------
# pip
# ---------------------------------------------------------------------------
PIP_PACKAGES = [
    "python-nmap",
    "scapy>=2.5.0",
    "requests>=2.28.0",
    "netaddr>=0.9.0",
    "dnspython>=2.4.0",
    "colorama>=0.4.6",
    "tqdm>=4.65.0",
    "jinja2>=3.1.0",
    "ldap3>=2.9.1",
    "pysnmp>=6.1.0",
    "impacket>=0.11.0",
    "cryptography>=42.0.0",
    "paramiko>=3.0.0",
    "openpyxl>=3.1.0",
    "selenium>=4.18.0",
    "webdriver-manager>=4.0.0",
    # ssh-audit — pip fallback for distros where the system package is absent
    # (Fedora, openSUSE, recent Debian-without-Kali-repos). Provides the
    # `ssh-audit` console_script.
    "ssh-audit>=3.1.0",
    # BloodHound.py — AD collector used in Phase 12 (AD assessment). The pip
    # package "bloodhound" is the Python collector; the apt "bloodhound"
    # package is the unrelated Neo4j/Electron GUI app — do NOT use apt here.
    "bloodhound>=1.7.0",
    # enumdb — removed from pip (no longer available at >=1.0.10).
    # Installed via git clone in install_git() instead.
]

def install_pip():
    banner("Phase: pip packages")
    pip = [sys.executable, "-m", "pip"]
    for pkg in PIP_PACKAGES:
        if _pip_installed(pkg):
            info(f"  ✓ {pkg} already installed")
            continue
        info(f"pip install {pkg} …")
        run(pip + ["install", "--break-system-packages", pkg], check=False)

# ---------------------------------------------------------------------------
# Go tools
# ---------------------------------------------------------------------------
GO_TOOLS = [
    ("github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",  "nuclei"),
    ("github.com/rverton/webanalyze/cmd/webanalyze@latest",       "webanalyze"),
    ("github.com/OJ/gobuster/v3@latest",                          "gobuster"),
    ("github.com/ropnop/kerbrute@latest",                          "kerbrute"),
]

OFFLINE_BUNDLE_URLS = {
    "webanalyze":  "https://raw.githubusercontent.com/pr0t31n/OfflineInstallers/main/webanalyze_offline_kali.tar.gz",
}

def find_go():
    go = shutil.which("go")
    if go:
        return go
    for p in ["/usr/local/go/bin/go", "/usr/lib/go/bin/go"]:
        if os.path.isfile(p):
            return p
    return None

def install_go():
    banner("Phase: go tools")
    go_bin = find_go()
    if not go_bin:
        note("go not found in PATH — skipping Go tool installation.")
        note("Install Go from https://go.dev/dl/ and re-run with --skip-apt --skip-pip --skip-git")
        return

    env = os.environ.copy()
    env["GOBIN"] = "/usr/local/bin"

    for pkg, name in GO_TOOLS:
        if shutil.which(name):
            info(f"{name} already installed — skipping")
            continue
        info(f"Installing {name} via go install …")
        run([go_bin, "install", pkg], check=False, env=env)

def _detect_arch():
    """Normalised architecture string: x86_64, aarch64, x86, armv7, or raw."""
    m = platform.machine().lower()
    if m in ("x86_64", "amd64"):
        return "x86_64"
    if m in ("aarch64", "arm64"):
        return "aarch64"
    if m in ("i386", "i686", "x86"):
        return "x86"
    if m.startswith("arm"):
        return "armv7"
    return m


def _pick_rustscan_asset(names, os_kind, system, arch):
    """
    Select the correct outer-zip filename from bee-san/RustScan release assets
    based on detected OS + arch. Returns the asset name or None.

    Asset map (current release naming):
      rustscan.deb.zip                  → apt + x86_64 (amd64 .deb inside)
      x86_64-linux-rustscan.tar.gz.zip  → Linux x86_64 (binary inside tar.gz)
      aarch64-linux-rustscan.zip        → Linux aarch64 (raw binary inside zip)
      x86-linux-rustscan.zip            → Linux x86 (raw binary)
      x86_64-macos-rustscan.tar.gz.zip  → macOS x86_64
      aarch64-macos-rustscan.tar.gz.zip → macOS aarch64
      x86_64-windows-rustscan.exe.zip   → Windows x86_64
      x86-windows-rustscan.exe.zip      → Windows x86
    """
    name_list = list(names)
    lc = {n.lower(): n for n in name_list}

    # Preferred on apt systems: native .deb (currently amd64 only)
    if os_kind == "apt" and arch == "x86_64":
        if "rustscan.deb.zip" in lc:
            return lc["rustscan.deb.zip"]

    if system == "Linux":
        candidates = {
            "x86_64":  ["x86_64-linux-rustscan.tar.gz.zip"],
            "aarch64": ["aarch64-linux-rustscan.zip"],
            "x86":     ["x86-linux-rustscan.zip"],
        }.get(arch, [])
        for c in candidates:
            if c in lc:
                return lc[c]

    if system == "Darwin":
        candidates = {
            "x86_64":  ["x86_64-macos-rustscan.tar.gz.zip"],
            "aarch64": ["aarch64-macos-rustscan.tar.gz.zip"],
        }.get(arch, [])
        for c in candidates:
            if c in lc:
                return lc[c]

    if system == "Windows":
        candidates = {
            "x86_64": ["x86_64-windows-rustscan.exe.zip"],
            "x86":    ["x86-windows-rustscan.exe.zip"],
        }.get(arch, [])
        for c in candidates:
            if c in lc:
                return lc[c]

    return None


def _copy_binary_to_path(directory, binary_name):
    """Find binary_name (or .exe) under directory and copy to /usr/local/bin."""
    candidates = (binary_name, f"{binary_name}.exe")
    for root, _, files in os.walk(directory):
        for f in files:
            if f in candidates:
                src  = os.path.join(root, f)
                dest = f"/usr/local/bin/{binary_name}"
                try:
                    shutil.copy2(src, dest)
                    os.chmod(dest, 0o755)
                    info(f"Installed {binary_name} → {dest}")
                    return True
                except Exception as e:
                    error(f"Install failed: {e}")
                    return False
    warn(f"Binary '{binary_name}' not found under {directory}")
    return False


def _install_unwrapped_rustscan(unwrap_dir):
    """Inspect unwrap_dir and install rustscan from whichever inner artifact is present."""
    import tarfile

    inner = []
    for root, _, files in os.walk(unwrap_dir):
        for f in files:
            inner.append(os.path.join(root, f))
    if not inner:
        error("Outer zip extracted to empty directory.")
        return False

    deb = next((p for p in inner if p.lower().endswith(".deb")), None)
    if deb:
        info(f"Inner .deb found: {os.path.basename(deb)}")
        subprocess.run(["dpkg", "-i", deb])
        info("Resolving dependencies with apt-get install -f -y …")
        subprocess.run(["apt-get", "install", "-f", "-y"])
        return shutil.which("rustscan") is not None

    rpm = next((p for p in inner if p.lower().endswith(".rpm")), None)
    if rpm:
        info(f"Inner .rpm found: {os.path.basename(rpm)}")
        if shutil.which("dnf"):
            subprocess.run(["dnf", "install", "-y", rpm])
        elif shutil.which("yum"):
            subprocess.run(["yum", "install", "-y", rpm])
        elif shutil.which("rpm"):
            subprocess.run(["rpm", "-ivh", "--replacepkgs", rpm])
        return shutil.which("rustscan") is not None

    tgz = next((p for p in inner if p.lower().endswith((".tar.gz", ".tgz"))), None)
    if tgz:
        info(f"Inner tarball found: {os.path.basename(tgz)}")
        ext_dir = os.path.join(unwrap_dir, "_tar_extract")
        os.makedirs(ext_dir, exist_ok=True)
        try:
            with tarfile.open(tgz) as tf:
                tf.extractall(ext_dir)
        except Exception as e:
            error(f"Tarball extraction failed: {e}")
            return False
        return _copy_binary_to_path(ext_dir, "rustscan")

    raw = next((p for p in inner
                if os.path.basename(p).lower() in ("rustscan", "rustscan.exe")), None)
    if raw:
        info(f"Raw binary found: {os.path.basename(raw)}")
        return _copy_binary_to_path(unwrap_dir, "rustscan")

    error(f"No installable rustscan artifact found in {unwrap_dir}")
    error(f"Contents: {[os.path.basename(p) for p in inner]}")
    return False


def install_rustscan_from_github():
    """
    Download rustscan from the official bee-san/RustScan GitHub release,
    matched to current OS + architecture. Assets are double-archived (outer
    .zip wraps the actual .deb / .tar.gz / raw binary / .exe).
    """
    import json
    import tempfile
    import urllib.request
    import zipfile

    arch   = _detect_arch()
    system = platform.system()
    info(f"GitHub fallback — OS={OS} system={system} arch={arch}")

    try:
        req = urllib.request.Request(
            "https://api.github.com/repos/bee-san/RustScan/releases/latest",
            headers={"User-Agent": "scattershot3-installer/1.0"},
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            rel = json.loads(r.read().decode())
    except Exception as e:
        warn(f"GitHub API query failed: {e}")
        return False

    version = rel.get("tag_name", "?")
    assets  = {a.get("name", ""): a for a in rel.get("assets", [])}
    info(f"Latest RustScan release: v{version} ({len(assets)} assets)")

    asset_name = _pick_rustscan_asset(assets.keys(), OS, system, arch)
    if not asset_name:
        warn(f"No matching asset for OS={OS} system={system} arch={arch}")
        warn(f"Available: {', '.join(assets.keys())}")
        return False

    url = assets[asset_name].get("browser_download_url", "")
    info(f"Selected asset: {asset_name}")

    with tempfile.TemporaryDirectory() as td:
        outer_zip = os.path.join(td, asset_name)
        info(f"Downloading {url} …")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "scattershot3-installer/1.0"})
            with urllib.request.urlopen(req, timeout=180) as r, open(outer_zip, "wb") as f:
                shutil.copyfileobj(r, f)
        except Exception as e:
            error(f"Download failed: {e}")
            return False

        unwrap_dir = os.path.join(td, "unwrap")
        os.makedirs(unwrap_dir, exist_ok=True)
        info("Unwrapping outer zip …")
        try:
            with zipfile.ZipFile(outer_zip) as zf:
                zf.extractall(unwrap_dir)
        except Exception as e:
            error(f"Outer zip extraction failed: {e}")
            return False

        ok = _install_unwrapped_rustscan(unwrap_dir)

    if ok and shutil.which("rustscan"):
        info(f"rustscan v{version} installed via GitHub release.")
        return True
    return False


def install_rustscan():
    """
    Multi-stage rustscan install chain:
      1. Already installed → skip
      2. Native package manager (apt-get / brew)            — fast, version-managed
      3. GitHub release download matched to OS + arch       — works everywhere
      4. cargo install rustscan                             — last resort (slow)
    """
    if shutil.which("rustscan"):
        info("rustscan already installed.")
        return

    if OS == "apt":
        info("Trying apt-get install rustscan …")
        run(["apt-get", "install", "-y", "rustscan"], check=False)
        if shutil.which("rustscan"):
            return
    elif OS == "macos" and shutil.which("brew"):
        info("Trying brew install rustscan …")
        brew_install("rustscan")
        if shutil.which("rustscan"):
            return

    if install_rustscan_from_github():
        return

    cargo = shutil.which("cargo")
    if cargo:
        info("Trying cargo install rustscan …")
        run([cargo, "install", "rustscan"], check=False)
        if shutil.which("rustscan"):
            return

    warn("rustscan installation failed via all fallbacks.")
    note("Manual install: https://github.com/bee-san/RustScan/releases")


def install_kerbrute():
    """Install kerbrute via apt (Kali) or go install fallback."""
    if shutil.which("kerbrute"):
        info("kerbrute already installed.")
        return
    if OS == "apt":
        info("Installing kerbrute via apt …")
        run(["apt-get", "install", "-y", "kerbrute"], check=False)
        if shutil.which("kerbrute"):
            return
    go_bin = find_go()
    if go_bin:
        info("Installing kerbrute via go install …")
        env = os.environ.copy()
        env["GOBIN"] = "/usr/local/bin"
        run([go_bin, "install", "github.com/ropnop/kerbrute@latest"],
            check=False, env=env)
    else:
        note("kerbrute not found and go not available — install manually: https://github.com/ropnop/kerbrute")


def install_odat():
    """Clone ODAT (Oracle Database Attack Tool) and install Python deps."""
    already = shutil.which("odat") or os.path.isfile("/opt/odat/odat.py")
    if already and os.path.isdir("/opt/odat"):
        info("odat already installed — pulling latest…")
        git_clone_or_update("https://github.com/quentinhardy/odat.git", "/opt/odat")
        return
    elif already:
        info("odat already installed (not a git clone).")
        return
    git_clone_or_update("https://github.com/quentinhardy/odat.git", "/opt/odat")
    info("Installing odat Python dependencies …")
    for dep in ["impacket", "colorlog", "cx_Oracle"]:
        if _pip_installed(dep):
            info(f"  ✓ {dep} already installed")
        else:
            run([sys.executable, "-m", "pip", "install", "--break-system-packages",
                 dep], check=False)
    odat_py = "/opt/odat/odat.py"
    if os.path.isfile(odat_py):
        os.chmod(odat_py, 0o755)
        symlink_force(odat_py, "/usr/local/bin/odat")


def install_msdat():
    """Clone MSDAT (Microsoft SQL Database Attack Tool) and install Python deps."""
    already = shutil.which("msdat") or os.path.isfile("/opt/msdat/msdat.py")
    if already and os.path.isdir("/opt/msdat"):
        info("msdat already installed — pulling latest…")
        git_clone_or_update("https://github.com/quentinhardy/msdat.git", "/opt/msdat")
        return
    elif already:
        info("msdat already installed (not a git clone).")
        return
    git_clone_or_update("https://github.com/quentinhardy/msdat.git", "/opt/msdat")
    info("Installing msdat Python dependencies …")
    for dep in ["impacket", "colorlog"]:
        if _pip_installed(dep):
            info(f"  ✓ {dep} already installed")
        else:
            run([sys.executable, "-m", "pip", "install", "--break-system-packages",
                 dep], check=False)
    msdat_py = "/opt/msdat/msdat.py"
    if os.path.isfile(msdat_py):
        os.chmod(msdat_py, 0o755)
        symlink_force(msdat_py, "/usr/local/bin/msdat")


def install_xsstrike():
    """Clone XSStrike and install Python deps."""
    if os.path.isdir("/opt/XSStrike"):
        info("XSStrike already installed — pulling latest…")
        git_clone_or_update("https://github.com/s0md3v/XSStrike.git", "/opt/XSStrike")
        return
    git_clone_or_update("https://github.com/s0md3v/XSStrike.git", "/opt/XSStrike")
    info("Installing XSStrike Python dependencies …")
    for dep in ["requests", "beautifulsoup4", "fuzzywuzzy"]:
        if _pip_installed(dep):
            info(f"  ✓ {dep} already installed")
        else:
            run([sys.executable, "-m", "pip", "install", "--break-system-packages",
                 dep], check=False)


def install_enumdb():
    """Clone enumdb and install via pip from the clone (PyPI package removed)."""
    if shutil.which("enumdb") and os.path.isdir("/opt/enumdb"):
        info("enumdb already installed — pulling latest…")
        git_clone_or_update("https://github.com/m8r0wn/enumdb.git", "/opt/enumdb")
        return
    elif shutil.which("enumdb"):
        info("enumdb already installed (not a git clone).")
        return
    git_clone_or_update("https://github.com/m8r0wn/enumdb.git", "/opt/enumdb")
    info("Installing enumdb from git clone …")
    result = run([sys.executable, "-m", "pip", "install", "--break-system-packages",
                  "/opt/enumdb"], check=False, capture=True)
    if not shutil.which("enumdb"):
        req = "/opt/enumdb/requirements.txt"
        if os.path.isfile(req):
            info("pip install did not produce enumdb binary; trying requirements.txt …")
            run([sys.executable, "-m", "pip", "install", "--break-system-packages",
                 "-r", req], check=False)
        for candidate in ("/opt/enumdb/enumdb/enumdb.py", "/opt/enumdb/enumdb.py"):
            if os.path.isfile(candidate):
                os.chmod(candidate, 0o755)
                symlink_force(candidate, "/usr/local/bin/enumdb")
                break

# ---------------------------------------------------------------------------
# Git tools
# ---------------------------------------------------------------------------
def git_clone_or_update(url, dest):
    if os.path.isdir(dest):
        info(f"Updating existing clone: {dest}")
        run(["git", "-C", dest, "pull", "--ff-only"], check=False)
    else:
        run(["git", "clone", url, dest])

def _safe(fn, label):
    try:
        fn()
    except Exception as e:
        error(f"{label} failed: {e}")
        note(f"Continuing with remaining tools …")


def install_git():
    banner("Phase: git tools")

    _safe(lambda: git_clone_or_update("https://github.com/santoru/shcheck.git", "/opt/shcheck"), "shcheck")

    def _adenum():
        git_clone_or_update("https://github.com/SecuProject/ADenum.git", "/opt/ADenum")
        info("Installing ADenum Python dependencies …")
        for dep in ["ldap3", "impacket", "gssapi"]:
            if _pip_installed(dep):
                info(f"  ✓ {dep} already installed")
            else:
                run([sys.executable, "-m", "pip", "install", "--break-system-packages",
                     dep], check=False)
    _safe(_adenum, "ADenum")

    _safe(lambda: git_clone_or_update("https://github.com/lgandx/Responder.git", "/opt/Responder"), "Responder")

    def _testssl():
        git_clone_or_update("https://github.com/drwetter/testssl.sh.git", "/opt/testssl.sh")
        testssl_bin = "/opt/testssl.sh/testssl.sh"
        if os.path.isfile(testssl_bin):
            os.chmod(testssl_bin, 0o755)
            symlink_force(testssl_bin, "/usr/local/bin/testssl.sh")
            info("testssl.sh symlinked to /usr/local/bin/testssl.sh")
    _safe(_testssl, "testssl.sh")

    _safe(lambda: git_clone_or_update("https://github.com/projectdiscovery/nuclei-templates.git", "/opt/nuclei-templates"), "nuclei-templates")

    _safe(install_rustscan, "rustscan")
    _safe(install_kerbrute, "kerbrute")
    _safe(install_odat, "odat")
    _safe(install_msdat, "msdat")
    _safe(install_xsstrike, "XSStrike")
    _safe(install_enumdb, "enumdb")
    _safe(install_vulners_nse, "vulners.nse")

# ---------------------------------------------------------------------------
# Vulners NSE script (CVE scoring for nmap -sV)
# ---------------------------------------------------------------------------
_NMAP_SCRIPT_DIRS = {
    "apt":     ["/usr/share/nmap/scripts", "/usr/local/share/nmap/scripts"],
    "dnf":     ["/usr/share/nmap/scripts"],
    "zypper":  ["/usr/share/nmap/scripts"],
    "macos":   ["/opt/homebrew/share/nmap/scripts", "/usr/local/share/nmap/scripts"],
    "windows": [r"C:\Program Files (x86)\Nmap\scripts",
                r"C:\Program Files\Nmap\scripts"],
}
_VULNERS_NSE_URL = (
    "https://raw.githubusercontent.com/vulnersCom/nmap-vulners/master/vulners.nse"
)


def install_vulners_nse():
    """Download vulners.nse into the first writable nmap scripts directory.

    Adds CVE scoring to nmap -sV output (consumed by Scattershot3's
    vulners NSE parser at scan time).
    """
    banner("Phase: vulners.nse")
    dirs = _NMAP_SCRIPT_DIRS.get(OS, [])
    if not dirs:
        note(f"No known nmap scripts directory for OS '{OS}' — skipping vulners.nse")
        return

    # Already installed?
    for d in dirs:
        p = os.path.join(d, "vulners.nse")
        if os.path.isfile(p):
            info(f"vulners.nse already installed at {p}")
            return

    # Pick the first directory that exists and is writable
    target = None
    for d in dirs:
        if os.path.isdir(d) and os.access(d, os.W_OK):
            target = os.path.join(d, "vulners.nse")
            break
    if not target:
        note(f"No writable nmap scripts dir found in {dirs} — skipping vulners.nse")
        note("    (Re-run install.py with sudo, or download manually.)")
        return

    info(f"Downloading vulners.nse → {target}")
    try:
        urllib.request.urlretrieve(_VULNERS_NSE_URL, target)
    except Exception as exc:
        warn(f"vulners.nse download failed: {exc}")
        return

    # Refresh nmap's script database so --script vulners works immediately
    nmap_bin = shutil.which("nmap")
    if nmap_bin:
        info("Updating nmap script database (nmap --script-updatedb) …")
        run([nmap_bin, "--script-updatedb"], check=False)
    info(f"vulners.nse installed: {target}")


# ---------------------------------------------------------------------------
# Metasploit Framework
# ---------------------------------------------------------------------------
def install_msfconsole():
    """Install msfconsole if not already present."""
    banner("Phase: Metasploit Framework")
    found = (shutil.which("msfconsole") or
             os.path.isfile("/usr/bin/msfconsole") or
             os.path.isfile("/usr/local/bin/msfconsole") or
             os.path.isfile("/opt/metasploit-framework/bin/msfconsole"))
    if found:
        info("msfconsole found — skipping installation.")
        return
    if OS == "apt":
        info("Installing metasploit-framework via apt …")
        run(["apt-get", "install", "-y", "metasploit-framework"], check=False)
    elif OS == "macos":
        info("Installing metasploit via brew cask …")
        brew_install("metasploit", cask=True)
    else:
        note("msfconsole not found. Install manually: https://docs.metasploit.com/docs/using-metasploit/getting-started/nightly-installers.html")

# ---------------------------------------------------------------------------
# Symlinks
# ---------------------------------------------------------------------------
APP_DIR   = "/opt/pr0t31n/Scattershot3"
APP_FILE  = f"{APP_DIR}/scattershot3.py"
SYMLINKS  = {
    "/usr/local/bin/scattershot3": APP_FILE,
    "/usr/local/bin/ss3":          APP_FILE,
}

def symlink_force(src, dest):
    try:
        if os.path.islink(dest) or os.path.exists(dest):
            os.remove(dest)
        os.symlink(src, dest)
        info(f"Symlink: {dest} -> {src}")
    except PermissionError:
        note(f"Cannot create symlink {dest} — not root.")
    except Exception as e:
        warn(f"Symlink {dest} failed: {e}")

def install_symlinks():
    banner("Creating symlinks")
    if not os.path.isfile(APP_FILE):
        warn(f"{APP_FILE} not found — symlinks will point to a missing target.")
    for dest, src in SYMLINKS.items():
        symlink_force(src, dest)

# ---------------------------------------------------------------------------
# Check / verify
# ---------------------------------------------------------------------------
VERIFY_TOOLS = [
    "nmap", "sslscan", "nuclei", "gobuster", "wpscan",
    "hydra", "enum4linux", "rpcclient", "smbmap", "smbclient",
    "snmpwalk", "searchsploit",
    "showmount", "ipmitool", "testssl.sh", "rustscan",
    "msfconsole", "nbtscan", "kerbrute", "sqlmap",
    "ike-scan",
]
VERIFY_PYTHON = [
    "nmap", "scapy", "requests", "colorama",
    "impacket", "ldap3", "openpyxl", "dns", "selenium",
    "bloodhound",
]

def run_check():
    banner("Post-install verification")
    print(f"\n{C}Binary tools:{W}")
    for tool in VERIFY_TOOLS:
        found = shutil.which(tool)
        if found:
            info(f"{tool:30s} {G}FOUND{W} ({found})")
        else:
            warn(f"{tool:30s} {Y}NOT FOUND{W}")

    print(f"\n{C}Python imports:{W}")
    for pkg in VERIFY_PYTHON:
        try:
            __import__(pkg)
            info(f"{pkg:30s} {G}OK{W}")
        except ImportError:
            warn(f"{pkg:30s} {Y}MISSING{W}")

    print(f"\n{C}Git tools:{W}")
    for path, label in [
        ("/opt/shcheck", "shcheck"),
        ("/opt/ADenum", "ADenum"),
        ("/opt/Responder", "Responder"),
        ("/opt/testssl.sh", "testssl.sh"),
        ("/opt/nuclei-templates", "nuclei-templates"),
        ("/opt/odat", "odat"),
        ("/opt/msdat", "msdat"),
        ("/opt/XSStrike", "XSStrike"),
        ("/opt/enumdb", "enumdb"),
    ]:
        if os.path.isdir(path):
            info(f"{label:30s} {G}PRESENT{W} ({path})")
        else:
            warn(f"{label:30s} {Y}NOT FOUND{W}")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
def print_summary(skips):
    banner("Post-install summary")
    info(f"Application : Scattershot3 — Network Pentest Orchestrator")
    info(f"Location    : {APP_DIR}")
    info(f"Symlinks    : scattershot3, ss3 → {APP_FILE}")
    info(f"OS detected : {OS}")
    print()
    phases = ["system", "pip", "go", "git"]
    for p in phases:
        status = f"{Y}SKIPPED{W}" if p in skips else f"{G}DONE{W}"
        print(f"  {p:10s} {status}")
    print()
    info("Run: scattershot3 --help   or   ss3 --help")
    note("chromedriver is managed automatically by webdriver-manager — do NOT install chromium-driver manually.")
    note("testssl.sh installed from git (/opt/testssl.sh) — apt version NOT installed (outdated).")
    note("gobuster installed via go install — apt version NOT installed (outdated).")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Scattershot3 installer")
    parser.add_argument("--skip-apt",    "--skip-system", dest="skip_system", action="store_true")
    parser.add_argument("--skip-pip",    action="store_true")
    parser.add_argument("--skip-go",     action="store_true")
    parser.add_argument("--skip-git",    action="store_true")
    parser.add_argument("--check",       action="store_true", help="Verify installation only")
    args = parser.parse_args()

    banner("Scattershot3 — Network Pentest Orchestrator — Installer")
    info(f"Detected OS : {OS}")
    info(f"Python      : {sys.executable}")

    if args.check:
        run_check()
        return

    skips = set()

    if not args.skip_system:
        install_system()
    else:
        skips.add("system"); note("Skipping system packages.")

    if not args.skip_pip:
        install_pip()
    else:
        skips.add("pip"); note("Skipping pip packages.")

    if not args.skip_go:
        install_go()
    else:
        skips.add("go"); note("Skipping go tools.")

    if not args.skip_git:
        install_git()
    else:
        skips.add("git"); note("Skipping git tools.")

    install_msfconsole()
    install_symlinks()
    run_check()
    print_summary(skips)

if __name__ == "__main__":
    main()
