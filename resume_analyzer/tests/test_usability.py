"""Tests for usability study scoring and export."""

import pytest

from resume_analyzer.services.storage.usability_service import (
    UsabilityService,
    compute_sus_score,
    docx_available,
)


def test_compute_sus_score_all_neutral() -> None:
    """Neutral 3 on all items yields mid-range SUS."""
    ratings = [3] * 10
    score = compute_sus_score(ratings)
    assert score == 50.0


def test_compute_sus_score_requires_ten_items() -> None:
    """SUS calculation rejects wrong length."""
    with pytest.raises(ValueError):
        compute_sus_score([3, 3, 3])


def test_compute_sus_score_range() -> None:
    """Best-case ratings produce high SUS."""
    ratings = [5, 1, 5, 1, 5, 1, 5, 1, 5, 1]
    score = compute_sus_score(ratings)
    assert score == 100.0


@pytest.mark.skipif(not docx_available(), reason="python-docx not installed")
def test_export_docx_bytes_produces_docx() -> None:
    """Word export returns a valid docx file (ZIP magic bytes)."""
    service = UsabilityService()
    data = service.export_docx_bytes()
    assert isinstance(data, bytes)
    assert len(data) > 100
    assert data[:2] == b"PK"
