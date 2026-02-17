from pathlib import Path

from app.models import ChangeRequest


DOCS_ROOT = Path(__file__).resolve().parents[2] / "docs" / "generated"


def ensure_docs_dir() -> Path:
    DOCS_ROOT.mkdir(parents=True, exist_ok=True)
    return DOCS_ROOT


def generate_change_request_docs(cr: ChangeRequest) -> dict[str, Path]:
    """
    Generate functional specification, SOP update, and release notes markdown files
    for a given change request under docs/generated/.
    """
    docs_dir = ensure_docs_dir()
    prefix = f"cr-{cr.id:04d}"

    functional_spec = docs_dir / f"{prefix}-functional-spec.md"
    sop_update = docs_dir / f"{prefix}-sop-update.md"
    release_notes = docs_dir / f"{prefix}-release-notes.md"

    functional_spec.write_text(
        f"# Functional Specification: {cr.title}\n\n"
        f"**Requested by:** {cr.requested_by}\n\n"
        f"## Current Process\n{cr.current_process}\n\n"
        f"## Proposed Change\n{cr.proposed_change}\n\n"
        f"## Impact Analysis\n\n"
        f"- Users: {cr.impact_users}\n"
        f"- Data: {cr.impact_data}\n"
        f"- Security: {cr.impact_security}\n",
        encoding="utf-8",
    )

    sop_update.write_text(
        f"# SOP Update: {cr.title}\n\n"
        f"## Overview\nThis document outlines updates to standard operating procedures "
        f"required to support the approved change request.\n\n"
        f"## New / Updated Steps\n\n{cr.proposed_change}\n",
        encoding="utf-8",
    )

    release_notes.write_text(
        f"# Release Notes: {cr.title}\n\n"
        f"## Summary\n{cr.proposed_change}\n\n"
        f"## Impacted Users\n{cr.impact_users}\n\n"
        f"## Deployment Notes\n- Coordinate with court operations and IT support.\n",
        encoding="utf-8",
    )

    return {
        "functional_spec": functional_spec,
        "sop_update": sop_update,
        "release_notes": release_notes,
    }

