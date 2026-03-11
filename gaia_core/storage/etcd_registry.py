"""etcd registry — consistent metadata, node registry, and continuity head pointers.

Dependency: etcd3 (optional, guarded import)
Key namespaces:
  /gaia/nodes/{node_id}          → node registration record
  /gaia/continuity/{node_id}/head → latest checkpoint sequence
  /gaia/leases/{node_id}         → liveness lease
  /gaia/routing/{service}        → runtime routing table
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from typing import Any

log = logging.getLogger(__name__)

try:
    import etcd3  # type: ignore
    _ETCD_AVAILABLE = True
except ImportError:
    _ETCD_AVAILABLE = False
    etcd3 = None  # type: ignore

NS_NODES = "/gaia/nodes"
NS_CONTINUITY = "/gaia/continuity"
NS_LEASES = "/gaia/leases"
NS_ROUTING = "/gaia/routing"


@dataclass
class NodeRecord:
    node_id: str
    hostname: str
    tier: str          # edge | laptop | desktop | server | meta
    cores: list[str]   # e.g. ["NEXUS", "GUARDIAN", "SOPHIA"]
    version: str
    timestamp_ns: int


class EtcdRegistry:
    """etcd-backed node registry and continuity head tracker."""

    def __init__(self, host: str = "localhost", port: int = 2379) -> None:
        if not _ETCD_AVAILABLE:
            raise ImportError("etcd3 package is required. Run: pip install etcd3")
        self._client = etcd3.client(host=host, port=port)

    # --- Node registration ---
    def register_node(self, record: NodeRecord, ttl: int = 30) -> None:
        key = f"{NS_NODES}/{record.node_id}"
        lease = self._client.lease(ttl)
        self._client.put(key, json.dumps(asdict(record)), lease=lease)
        log.info("Registered node %s (tier=%s)", record.node_id, record.tier)

    def get_node(self, node_id: str) -> NodeRecord | None:
        key = f"{NS_NODES}/{node_id}"
        value, _ = self._client.get(key)
        if value is None:
            return None
        return NodeRecord(**json.loads(value))

    def list_nodes(self) -> list[NodeRecord]:
        results = []
        for value, _ in self._client.get_prefix(NS_NODES + "/"):
            if value:
                results.append(NodeRecord(**json.loads(value)))
        return results

    # --- Continuity head pointers ---
    def set_head(self, node_id: str, sequence: int) -> None:
        key = f"{NS_CONTINUITY}/{node_id}/head"
        self._client.put(key, str(sequence))
        log.debug("Set continuity head: node=%s seq=%d", node_id, sequence)

    def get_head(self, node_id: str) -> int | None:
        key = f"{NS_CONTINUITY}/{node_id}/head"
        value, _ = self._client.get(key)
        return int(value) if value else None

    # --- Generic KV ---
    def put(self, key: str, value: Any) -> None:
        self._client.put(key, json.dumps(value))

    def get(self, key: str) -> Any:
        value, _ = self._client.get(key)
        return json.loads(value) if value else None
