from __future__ import annotations

from pathlib import Path

import structlog

from adip.data_import.importers.base import BaseImporter
from adip.data_import.readers import read_text
from adip.data_import.statistics import ImportStats
from adip.utils.file_utils import list_files, safe_read_bytes

log = structlog.get_logger(__name__)


class KnowledgeImporter(BaseImporter):
    """Phase 4: Import knowledge documents (articles, playbooks, SOPs, best practices, manuals)."""

    @property
    def phase_name(self) -> str:
        return "KNOWLEDGE"

    def run(self) -> ImportStats:
        self.timer.start()
        self.stats.phase = self.phase_name

        log.info("import.phase.knowledge.start")

        self._import_text_docs("knowledge_base/knowledge_articles", "ARTICLE")
        self._import_text_docs("knowledge_base/playbooks", "PLAYBOOK")
        self._import_text_docs("knowledge_base/sops", "SOP")
        self._import_text_docs("knowledge_base/best_practices", "BEST_PRACTICE")
        self._import_pdf_manuals("knowledge_base/equipment_manuals")

        self.timer.stop()
        self.stats.execution_time_seconds = self.timer.elapsed
        log.info("import.phase.knowledge.complete", stats=self.stats.to_dict())
        return self.stats

    def _import_text_docs(self, relative_dir: str, doc_type: str) -> None:
        dir_path = self.resolve_path(relative_dir)
        if not dir_path.is_dir():
            log.warning("import.directory_not_found", path=str(dir_path))
            return

        files = list_files(dir_path, "*.txt")
        imported = 0
        for fpath in files:
            content = read_text(fpath)
            if not content:
                continue
            fname = fpath.name
            if self._is_duplicate_doc(fname, content):
                self.stats.duplicates += 1
                continue
            self.stats.imported += 1
            imported += 1

        self.stats.total_records += len(files)
        self.stats.file_breakdown[relative_dir] = {
            "total": len(files),
            "imported": imported,
        }
        log.info("import.text_docs", directory=relative_dir, type=doc_type, imported=imported, total=len(files))

    def _import_pdf_manuals(self, relative_dir: str) -> None:
        dir_path = self.resolve_path(relative_dir)
        if not dir_path.is_dir():
            log.warning("import.directory_not_found", path=str(dir_path))
            return

        files = list_files(dir_path, "*.pdf")
        imported = 0
        for fpath in files:
            content = safe_read_bytes(fpath)
            if not content:
                continue
            fname = fpath.name
            if self._is_duplicate_doc(fname, str(len(content))):
                continue
            self.stats.imported += 1
            imported += 1

        self.stats.total_records += len(files)
        self.stats.file_breakdown[relative_dir] = {
            "total": len(files),
            "imported": imported,
        }
        log.info("import.pdf_manuals", directory=relative_dir, imported=imported, total=len(files))

    def _is_duplicate_doc(self, fname: str, content: str) -> bool:
        return self.dedup.is_duplicate_by_hash({"fname": fname, "content_len": str(len(content))})
