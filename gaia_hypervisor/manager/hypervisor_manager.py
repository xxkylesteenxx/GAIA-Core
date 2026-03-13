"""
HypervisorManager — Unified VM + Container Runtime
Layer 13: GAIA-Hypervisor

One API for two guest types:
  - Full OS guests  (Windows, macOS, Ubuntu, …) via KVM/QEMU (libvirt)
  - AI / lightweight guests (Grok, Claude, Llama, …) via Podman containers

GUARDIAN monitors every live guest.
All resource limits are Viriditas-aware (tied to the consciousness-aware scheduler).

Dependencies (install separately — not auto-imported at module level):
  pip install libvirt-python podman
"""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from typing import Any

logger = logging.getLogger(__name__)

# Guest type classification keywords
_FULL_OS_KEYWORDS = {"windows", "macos", "ubuntu", "debian", "fedora", "arch", "dos"}


class HypervisorManager:
    """
    Unified runtime engine for GAIA-Hypervisor.

    Uses lazy imports for libvirt and podman so the module loads cleanly
    in environments where the hypervisor stack is not yet installed
    (e.g., CI, documentation builds, GAIA-IoT edge devices).
    """

    def __init__(self, libvirt_uri: str = "qemu:///system"):
        self._libvirt_uri = libvirt_uri
        self._libvirt_conn = None   # opened lazily
        self._podman_client = None  # opened lazily
        logger.info("HypervisorManager initialised (libvirt_uri=%s)", libvirt_uri)

    # ------------------------------------------------------------------
    # Lazy connection helpers
    # ------------------------------------------------------------------

    @property
    def libvirt_conn(self):
        if self._libvirt_conn is None:
            import libvirt  # noqa: PLC0415
            self._libvirt_conn = libvirt.open(self._libvirt_uri)
        return self._libvirt_conn

    @property
    def podman_client(self):
        if self._podman_client is None:
            import podman  # noqa: PLC0415
            self._podman_client = podman.PodmanClient()
        return self._podman_client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def launch_sandboxed(
        self, package_url: str, intent: str
    ) -> dict[str, Any]:
        """
        Launch a package as either a VM or a container.

        Full OS keywords in the URL → KVM virtual machine.
        Everything else           → Podman container.

        Args:
            package_url: URI or image reference of the .gaia package.
            intent:      Human-readable purpose string (logged, not executed).

        Returns:
            dict with keys: status, guest_type, package_url.
        """
        guest_type = self._classify_guest(package_url)
        logger.info(
            "Launching %s guest: %s | intent=%r", guest_type, package_url, intent
        )

        if guest_type == "vm":
            return self._launch_vm(package_url)
        return self._launch_container(package_url)

    # ------------------------------------------------------------------
    # Private launch methods
    # ------------------------------------------------------------------

    def _classify_guest(self, package_url: str) -> str:
        """Return 'vm' for full OS images, 'container' otherwise."""
        lower = package_url.lower()
        if any(kw in lower for kw in _FULL_OS_KEYWORDS):
            return "vm"
        return "container"

    def _launch_vm(self, package_url: str) -> dict[str, Any]:
        """Boot a full OS guest via KVM/QEMU."""
        xml = self._build_qemu_xml(package_url)
        try:
            conn = self.libvirt_conn
            domain = conn.createXML(xml, 0)
            domain.create()
            self._guardian_watch(domain)
            return {"status": "running", "guest_type": "vm", "package_url": package_url}
        except Exception as exc:  # noqa: BLE001
            logger.error("VM launch failed for %s: %s", package_url, exc)
            raise

    def _launch_container(self, package_url: str) -> dict[str, Any]:
        """Run an AI agent or lightweight guest as a Podman container."""
        try:
            client = self.podman_client
            container = client.containers.run(
                image=package_url,
                detach=True,
                security_opt=["no-new-privileges"],
                # Viriditas-aware CPU quota: placeholder for consciousness-aware
                # scheduler integration (GAIA energy optimization spec §3.2).
                cpu_quota=50000,  # 50 % of one core — overridden by scheduler
            )
            self._guardian_watch(container)
            return {
                "status": "running",
                "guest_type": "container",
                "package_url": package_url,
            }
        except Exception as exc:  # noqa: BLE001
            logger.error("Container launch failed for %s: %s", package_url, exc)
            raise

    # ------------------------------------------------------------------
    # GUARDIAN integration
    # ------------------------------------------------------------------

    @staticmethod
    def _guardian_watch(guest: Any) -> None:
        """Hand the live guest to GUARDIAN for continuous monitoring."""
        try:
            from gaia_core.guardian import GUARDIAN  # noqa: PLC0415
            GUARDIAN.monitor_runtime(guest)
        except ImportError:
            logger.warning(
                "GUARDIAN not available — guest running without Codex monitoring. "
                "Install gaia_core to enable full enforcement."
            )

    # ------------------------------------------------------------------
    # QEMU XML builder
    # ------------------------------------------------------------------

    @staticmethod
    def _build_qemu_xml(package_url: str) -> str:
        """
        Build a minimal libvirt domain XML for a QEMU/KVM guest.

        This is intentionally minimal — production deployments should
        extend with virtio devices, UEFI firmware, and SPICE/VNC display
        as defined in the GAIA Hypervisor Variant Spec (RTOS/Desktop/Server).
        """
        root = ET.Element("domain", type="kvm")
        ET.SubElement(root, "name").text = "gaia-guest"
        ET.SubElement(root, "memory", unit="MiB").text = "2048"
        ET.SubElement(root, "vcpu").text = "2"

        os_elem = ET.SubElement(root, "os")
        ET.SubElement(os_elem, "type", arch="x86_64", machine="q35").text = "hvm"

        devices = ET.SubElement(root, "devices")
        disk = ET.SubElement(devices, "disk", type="file", device="disk")
        ET.SubElement(disk, "driver", name="qemu", type="qcow2")
        ET.SubElement(disk, "source", file=package_url)
        ET.SubElement(disk, "target", dev="vda", bus="virtio")

        return ET.tostring(root, encoding="unicode")
