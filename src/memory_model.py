"""
Tier 1 Higher-Fidelity Memory Model for EP-GRM Simulator.

[MODULE STATUS: TIER 1 HARDENED - ALL ITEMS]
[PHASE 10 / REALIZATION PATH]

Purpose:
- Move beyond crude per-node "loaded" proxy.
- Model explicit memory pages / blocks.
- Realistic movement accounting: cache-line or page granularity.
- Prepare for persistence modeling and hierarchy costs.

Assumptions for Tier 1 (configurable later):
- Cache line size: 64 bytes (common)
- Page size: 4 KiB (common OS page)
- Each node has a base size + attribute overhead.
- "Bringing in" a node may cause page faults if not resident.

This is still a simulation, but much closer to real hardware costs than the original proxy.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Set, Optional
import math


@dataclass
class Page:
    """Represents a memory page/block."""
    page_id: int
    size: int = 4096  # 4KB default
    resident_nodes: Set[str] = field(default_factory=set)
    dirty: bool = False
    last_access: int = 0


class PageBasedMemory:
    """
    Tier 1 Memory subsystem for the EP-GRM simulator.

    Responsibilities:
    - Map nodes to pages (simple hash or round-robin for starters).
    - Track resident pages.
    - Compute realistic movement cost on access (page faults).
    - Future: hierarchy levels (L1 cache, DRAM, NVM), write amplification, etc.

    [LABEL: TIER 1 HIGHER FIDELITY]
    """

    def __init__(self,
                 page_size: int = 4096,
                 cache_line_size: int = 64,
                 node_overhead: int = 64,
                 l1_size: int = 32768,  # 32KB L1-like fast
                 dram_cost_mult: float = 1.0,
                 nvm_cost_mult: float = 3.0):
        self.page_size = page_size
        self.cache_line_size = cache_line_size
        self.node_overhead = node_overhead

        self.pages: Dict[int, Page] = {}
        self.node_to_page: Dict[str, int] = {}
        self.next_page_id: int = 0
        self.total_bytes_moved: int = 0
        self.page_faults: int = 0
        self.access_counter: int = 0

        # [PUSH ENVELOPE] Multi-level hierarchy
        self.l1_size = l1_size
        self.l1_resident: Set[int] = set()  # page_ids in "L1"
        self.dram_cost_mult = dram_cost_mult
        self.nvm_cost_mult = nvm_cost_mult

        # Persistence
        self.persistence_log = []
        self.write_backs = 0

    def _get_or_create_page(self, node_id: str, node_size: int) -> int:
        if node_id in self.node_to_page:
            return self.node_to_page[node_id]

        # Tier 1: try to pack into existing page with space
        for page_id, page in self.pages.items():
            if getattr(page, 'used_space', 0) + node_size <= page.size:
                page.used_space = getattr(page, 'used_space', 0) + node_size
                self.node_to_page[node_id] = page_id
                return page_id

        # Allocate new page
        page_id = self.next_page_id
        self.next_page_id += 1
        page = Page(page_id=page_id, size=self.page_size)
        page.used_space = node_size
        self.pages[page_id] = page
        self.node_to_page[node_id] = page_id
        return page_id

    def estimate_node_size(self, attrs: dict) -> int:
        """Rough size of a node including attributes."""
        base = self.node_overhead
        for k, v in attrs.items():
            base += len(str(k)) + len(str(v)) + 8  # crude
        return base

    def access_node(self, node_id: str, attrs: dict, is_write: bool = False) -> int:
        """
        Simulate access to a node. Pushes envelope with LRU eviction, hierarchy costs.

        Returns: number of bytes moved (with multipliers for levels).
        """
        self.access_counter += 1
        node_size = self.estimate_node_size(attrs)
        page_id = self._get_or_create_page(node_id, node_size)
        page = self.pages[page_id]

        bytes_moved = 0
        cost_mult = self.dram_cost_mult

        if node_id not in page.resident_nodes:
            self.page_faults += 1

            # LRU eviction if needed for L1
            if page_id not in self.l1_resident and len(self.l1_resident) * self.page_size > self.l1_size:
                # Evict oldest
                if self.l1_resident:
                    oldest = min(self.l1_resident, key=lambda p: self.pages[p].last_access if p in self.pages else 0)
                    self.l1_resident.remove(oldest)
                    if self.pages[oldest].dirty:
                        wb = len(self.pages[oldest].resident_nodes) * self.cache_line_size
                        self.total_bytes_moved += wb * self.nvm_cost_mult
                        self.write_backs += 1
                        self.persistence_log.append({'page': oldest, 'size': wb, 'type': 'evict'})

            lines_needed = max(1, math.ceil(node_size / self.cache_line_size))
            base_move = lines_needed * self.cache_line_size
            bytes_moved = int(base_move * cost_mult)

            page.resident_nodes.add(node_id)
            page.last_access = self.access_counter
            self.l1_resident.add(page_id)

            if is_write:
                page.dirty = True

            self.total_bytes_moved += bytes_moved

        elif is_write:
            page.dirty = True
            bytes_moved = int(self.cache_line_size * self.nvm_cost_mult)
            self.total_bytes_moved += bytes_moved

        # Simulate NVM persistence hit on write
        if is_write and page_id not in self.l1_resident:
            bytes_moved += int(self.cache_line_size * (self.nvm_cost_mult - 1))

        return bytes_moved

    def evict_page(self, page_id: int) -> int:
        """Simulate eviction. Returns bytes written back if dirty."""
        if page_id not in self.pages:
            return 0
        page = self.pages[page_id]
        written = 0
        if page.dirty:
            written = len(page.resident_nodes) * self.cache_line_size  # rough
        page.resident_nodes.clear()
        page.dirty = False
        return written

    def get_stats(self) -> dict:
        return {
            "total_bytes_moved": self.total_bytes_moved,
            "page_faults": self.page_faults,
            "write_backs": self.write_backs,
            "persistence_log_entries": len(self.persistence_log),
            "l1_pages": len(self.l1_resident),
            "pages_allocated": len(self.pages),
            "nodes_tracked": len(self.node_to_page),
        }

    def reset(self):
        self.pages.clear()
        self.node_to_page.clear()
        self.next_page_id = 0
        self.total_bytes_moved = 0
        self.page_faults = 0
        self.access_counter = 0
        if hasattr(self, 'write_backs'):
            self.write_backs = 0
        if hasattr(self, 'persistence_log'):
            self.persistence_log = []

    # [TIER 1 HARDENING] Dirty write-back and persistence
    def flush_dirty_pages(self, persist: bool = True) -> int:
        """Evict all dirty pages, optionally persisting to log. Returns bytes written."""
        written = 0
        for page_id, page in list(self.pages.items()):
            if page.dirty:
                wb = len(page.resident_nodes) * self.cache_line_size
                written += wb
                if persist:
                    self.persistence_log.append({
                        'page_id': page_id,
                        'size': wb,
                        'access': self.access_counter,
                        'nodes': len(page.resident_nodes),
                        'type': 'flush'
                    })
                page.dirty = False
                self.write_backs += 1
                # keep page resident but clean
        return written

    # [TIER 1 HARDENING] Hierarchy now integrated in access_node; this is alias for compatibility
    def access_node_with_hierarchy(self, node_id: str, attrs: dict, is_write: bool = False) -> int:
        return self.access_node(node_id, attrs, is_write)
