"""Unit tests for gaia_core.storage models and schema validation."""
import pytest
from gaia_core.storage.minio_store import CheckpointMeta, GAIA_BUCKETS
from gaia_core.storage.etcd_registry import NodeRecord, NS_NODES, NS_CONTINUITY
from gaia_core.storage.jetstream_log import CausalEvent, GAIA_STREAMS


def test_gaia_buckets_complete():
    expected = {
        "gaia-checkpoints", "gaia-evidence", "gaia-observations",
        "gaia-model-manifests", "gaia-sync-bundles", "gaia-twins",
    }
    assert set(GAIA_BUCKETS) == expected


def test_gaia_streams_complete():
    expected = {
        "GAIA.CAUSAL", "GAIA.OBSERVATION", "GAIA.ACTION",
        "GAIA.GUARDIAN", "GAIA.SYNC", "GAIA.CHECKPOINT",
    }
    assert set(GAIA_STREAMS) == expected


def test_causal_event_auto_timestamp():
    event = CausalEvent(stream="GAIA.CAUSAL", subject="gaia.causal.test", payload={"x": 1})
    assert event.timestamp_ns > 0


def test_causal_event_explicit_timestamp():
    event = CausalEvent(stream="GAIA.CAUSAL", subject="gaia.causal.test", payload={}, timestamp_ns=12345)
    assert event.timestamp_ns == 12345


def test_node_record_fields():
    import time
    record = NodeRecord(
        node_id="node-001",
        hostname="gaia-dev",
        tier="desktop",
        cores=["NEXUS", "GUARDIAN", "SOPHIA"],
        version="0.1.0",
        timestamp_ns=time.time_ns(),
    )
    assert record.tier == "desktop"
    assert "NEXUS" in record.cores


def test_etcd_namespaces():
    assert NS_NODES == "/gaia/nodes"
    assert NS_CONTINUITY == "/gaia/continuity"


def test_checkpoint_meta_fields():
    meta = CheckpointMeta(
        node_id="node-001",
        sequence=42,
        sha256="abc123",
        size_bytes=1024,
        timestamp_ns=999,
    )
    assert meta.sequence == 42
    assert meta.sha256 == "abc123"
