import pytest
from fastapi.testclient import TestClient
import main  # assumes your FastAPI app is in main.py

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def stub_parse_and_render(monkeypatch):
    """
    Stub out parse_amr and amr_to_svg so we don't invoke heavy models.
    """
    dummy_amr = "(x / dummy)"
    monkeypatch.setattr(main, "parse_amr", lambda text: dummy_amr)
    monkeypatch.setattr(main, "amr_to_svg", lambda amr: "<svg></svg>")


def test_process_amr_consistency_fields():
    payload = {"summary": "Hello world.", "article": "Hello world."}
    resp = client.post("/process_amr", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    # ensure new fields are present
    assert "consistency_score" in data
    assert "is_consistent" in data

    # perfect match → score == 1.0, is_consistent True
    assert data["consistency_score"] == 1.0
    assert data["is_consistent"] is True


def test_process_amr_bad_input():
    # missing summary
    resp = client.post("/process_amr", json={"summary": "", "article": "X"})
    assert resp.status_code == 400

    # missing article
    resp = client.post("/process_amr", json={"summary": "X", "article": ""})
    assert resp.status_code == 400

    # too long
    long_text = "a" * (main.MAX_SUMMARY_LENGTH + 1)
    resp = client.post("/process_amr", json={"summary": long_text, "article": "X"})
    assert resp.status_code == 400
