#!/usr/bin/env python3
"""
Render API Python Client - Zero Dependencies
Config: config.json (mode: json|env) or RENDER_API_KEY[S] env vars
"""

import os, sys, json, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR.parent / "config.json"
API_BASE = "https://api.render.com/v1"


class RenderError(Exception):
    def __init__(self, code, msg):
        self.code = code
        super().__init__(f"HTTP {code}: {msg}")


class RenderClient:
    """
    Render API Client. Free plan API keys work for all core operations.

    Usage:
        client = RenderClient()  # Uses config.json or env vars
        client = RenderClient(profile="company")
        client = RenderClient(api_key="rnd_xxx")
    """

    def __init__(self, api_key=None, profile=None):
        self.api_key = api_key or self._load_key(profile)
        self.profile = profile or "default"

    def _load_key(self, profile=None):
        # Try config file
        if CONFIG_FILE.exists():
            try:
                cfg = json.loads(CONFIG_FILE.read_text())
                if cfg.get("mode") == "json":
                    profile = profile or cfg.get("default_profile", "default")
                    profiles = cfg.get("profiles", {})
                    if profile in profiles:
                        key = profiles[profile].get("api_key", "")
                        if key and key != "rnd_YOUR_API_KEY_HERE":
                            self.profile = profile
                            return key
            except: pass

        # Env vars
        if keys := os.environ.get("RENDER_API_KEYS"):
            return keys.split(",")[0].strip()
        if key := os.environ.get("RENDER_API_KEY"):
            return key
        raise ValueError("No API key. Set RENDER_API_KEY or create config.json")

    def _req(self, method, endpoint, data=None, params=None):
        url = f"{API_BASE}{endpoint}"
        if params:
            qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
            if qs: url = f"{url}?{qs}"

        headers = {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}
        body = None
        if data:
            headers["Content-Type"] = "application/json"
            body = json.dumps(data).encode()

        try:
            with urlopen(Request(url, data=body, headers=headers, method=method)) as r:
                return json.loads(r.read().decode() or "{}")
        except HTTPError as e:
            msg = e.read().decode()
            if e.code == 401: msg += " (Free plan keys work fine)"
            if e.code == 403: msg += " (May need paid plan)"
            raise RenderError(e.code, msg)

    # Services
    def list_services(self, limit=20): return self._req("GET", "/services", params={"limit": limit})
    def get_service(self, id): return self._req("GET", f"/services/{id}")
    def suspend(self, id): return self._req("POST", f"/services/{id}/suspend")
    def resume(self, id): return self._req("POST", f"/services/{id}/resume")
    def restart(self, id): return self._req("POST", f"/services/{id}/restart")

    # Deploys
    def list_deploys(self, svc, limit=10): return self._req("GET", f"/services/{svc}/deploys", params={"limit": limit})
    def deploy(self, svc, clear=False): return self._req("POST", f"/services/{svc}/deploys", {"clearCache": "clear" if clear else "do_not_clear"})
    def cancel_deploy(self, svc, dep): return self._req("POST", f"/services/{svc}/deploys/{dep}/cancel")
    def rollback(self, svc, dep): return self._req("POST", f"/services/{svc}/rollback", {"deployId": dep})

    # Postgres (free: 30-day expiration)
    def list_postgres(self): return self._req("GET", "/postgres")
    def get_postgres(self, id): return self._req("GET", f"/postgres/{id}")
    def postgres_conn(self, id): return self._req("GET", f"/postgres/{id}/connection-info")

    # Key Value (free: ephemeral)
    def list_kv(self): return self._req("GET", "/key-value")
    def get_kv(self, id): return self._req("GET", f"/key-value/{id}")
    def kv_conn(self, id): return self._req("GET", f"/key-value/{id}/connection-info")

    # Other
    def list_env_vars(self, svc): return self._req("GET", f"/services/{svc}/env-vars")
    def set_env_var(self, svc, key, val): return self._req("PUT", f"/services/{svc}/env-vars/{key}", {"value": val})
    def logs(self, svc, limit=50): return self._req("GET", "/logs", params={"resource": svc, "limit": limit})
    def workspaces(self): return self._req("GET", "/owners")
    def list_jobs(self, svc): return self._req("GET", f"/services/{svc}/jobs")
    def create_job(self, svc, cmd): return self._req("POST", f"/services/{svc}/jobs", {"startCommand": cmd})
    def blueprints(self): return self._req("GET", "/blueprints")
    def sync_blueprint(self, id): return self._req("POST", f"/blueprints/{id}/sync")
    def domains(self, svc): return self._req("GET", f"/services/{svc}/custom-domains")
    def add_domain(self, svc, name): return self._req("POST", f"/services/{svc}/custom-domains", {"name": name})


def batch_op(op):
    """Run operation across all profiles/keys."""
    results = {}
    if CONFIG_FILE.exists():
        try:
            cfg = json.loads(CONFIG_FILE.read_text())
            if cfg.get("mode") == "json":
                for name, p in cfg.get("profiles", {}).items():
                    key = p.get("api_key", "")
                    if key and key != "rnd_YOUR_API_KEY_HERE":
                        try: results[name] = op(RenderClient(api_key=key))
                        except Exception as e: results[name] = {"error": str(e)}
                return results
        except: pass

    if keys := os.environ.get("RENDER_API_KEYS"):
        for i, k in enumerate(keys.split(",")):
            try: results[f"key-{i}"] = op(RenderClient(api_key=k.strip()))
            except Exception as e: results[f"key-{i}"] = {"error": str(e)}
    return results


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Render API CLI")
    p.add_argument("cmd", help="Command: services|postgres|kv|workspaces|deploy|logs|batch")
    p.add_argument("args", nargs="*")
    p.add_argument("-p", "--profile")
    args = p.parse_args()

    try:
        if args.cmd == "batch":
            sub = args.args[0] if args.args else "services"
            op = {"services": lambda c: c.list_services(), "workspaces": lambda c: c.workspaces()}.get(sub)
            if op: print(json.dumps(batch_op(op), indent=2))
            else: print("batch: services|workspaces", file=sys.stderr)
        else:
            c = RenderClient(profile=args.profile)
            r = {
                "services": lambda: c.list_services(),
                "postgres": lambda: c.list_postgres(),
                "kv": lambda: c.list_kv(),
                "workspaces": lambda: c.workspaces(),
                "deploy": lambda: c.deploy(args.args[0]) if args.args else None,
                "logs": lambda: c.logs(args.args[0]) if args.args else None,
            }.get(args.cmd, lambda: None)()
            if r: print(json.dumps(r, indent=2))
    except (ValueError, RenderError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
