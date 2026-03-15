"""Static compliance checks for GAIA PQC production files."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List
import json


@dataclass(slots=True)
class CheckResult:
    component: str
    control: str
    status: str
    details: Dict[str, object]

    def to_record(self) -> Dict[str, object]:
        return {
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "component": self.component,
            "control": self.control,
            "status": self.status,
            "details": self.details,
            "evidence": [],
        }


def check_openssl_groups(openssl_cnf_path: str | Path) -> CheckResult:
    content = Path(openssl_cnf_path).read_text(encoding="utf-8")
    groups_line = next((line for line in content.splitlines() if line.strip().startswith("Groups =")), "")
    required = ["X25519MLKEM768", "X25519"]
    missing = [value for value in required if value not in groups_line]
    return CheckResult(
        component="openssl",
        control="tls_groups",
        status="pass" if not missing else "fail",
        details={"groups_line": groups_line, "missing": missing},
    )


def check_tls13_only(openssl_cnf_path: str | Path) -> CheckResult:
    content = Path(openssl_cnf_path).read_text(encoding="utf-8")
    min_ok = "MinProtocol = TLSv1.3" in content
    max_ok = "MaxProtocol = TLSv1.3" in content
    return CheckResult(
        component="openssl",
        control="tls13_only",
        status="pass" if min_ok and max_ok else "fail",
        details={"min_ok": min_ok, "max_ok": max_ok},
    )


def check_istio_strict_mtls(overlay_path: str | Path) -> CheckResult:
    content = Path(overlay_path).read_text(encoding="utf-8")
    ok = "mode: STRICT" in content
    return CheckResult(
        component="istio",
        control="strict_mtls",
        status="pass" if ok else "fail",
        details={"contains_strict": ok, "path": str(overlay_path)},
    )


def run_all(root: str | Path) -> List[Dict[str, object]]:
    root = Path(root)
    results = [
        check_openssl_groups(root / "security/pqc/openssl/openssl.cnf"),
        check_tls13_only(root / "security/pqc/openssl/openssl.cnf"),
        check_istio_strict_mtls(root / "security/pqc/istio/ambient-pqc-overlay.yaml"),
        check_istio_strict_mtls(root / "security/pqc/istio/sidecar-pqc-overlay.yaml"),
    ]
    return [result.to_record() for result in results]


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[3]
    print(json.dumps(run_all(repo_root), indent=2))
