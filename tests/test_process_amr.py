import pytest
from fastapi.testclient import TestClient

# main.py のモジュールをインポートして、その中の名前をパッチターゲットとする
from amrsummarizer import main as main_module_under_test 
from amrsummarizer.main import app # FastAPI アプリケーション

client = TestClient(app)

@pytest.fixture(autouse=True)
def stub_all_heavy_processing(monkeypatch):
    """
    Stub out AMR parsing, SVG rendering, and factual consistency checking
    by patching them in the namespace of the module under test (main.py).
    """

    # 1. Stub for parse_amr (main_module_under_test.parse_amr をパッチ)
    class MockAMRGraph: # このスタブの内部構造は、スタブ関数が利用しない限り単純でOK
        def __init__(self, text="dummy amr graph for test"):
            self.text = text
            self.metadata = {} 
        def __str__(self):
            return self.text
    dummy_graph_instance = MockAMRGraph()
    monkeypatch.setattr(main_module_under_test, "parse_amr", lambda text: dummy_graph_instance)

    # 2. Stub for amr_to_svg (main_module_under_test.amr_to_svg をパッチ)
    dummy_svg_output = "<svg><text>Stubbed AMR SVG</text></svg>"
    monkeypatch.setattr(main_module_under_test, "amr_to_svg", lambda graph_obj: dummy_svg_output)

    # 3. Stub for is_factually_consistent (main_module_under_test.is_factually_consistent をパッチ)
    dummy_is_consistent_val = True
    dummy_consistency_score_val = 0.77 # スタブ用のダミースコア
    
    monkeypatch.setattr(
        main_module_under_test, 
        "is_factually_consistent", 
        # main.py での呼び出し時のシグネチャに合わせる
        lambda summary_amr, source_amrs, threshold: (dummy_is_consistent_val, dummy_consistency_score_val)
    )

# テスト関数 (変更なし、ただしアサーションはスタブの値を期待するようにする)
def test_process_amr_consistency_fields():
    payload = {"summary": "Hello world.", "article": "Hello world."}
    resp = client.post("/process_amr", json=payload)
    
    if resp.status_code == 500:
        # 念のため残しておきますが、今回の修正で500エラーは出なくなるはずです
        print("Server Error Response (test_process_amr_consistency_fields):", resp.text) 
        
    assert resp.status_code == 200 # まず200 OKであることを確認
    data = resp.json()

    # スタブが正しく機能しているかを確認するために、スタブの値をアサートする
    assert "summary_svg" in data
    assert data["summary_svg"] == "<svg><text>Stubbed AMR SVG</text></svg>" # ★スタブされたSVGを期待

    assert "top_sentence_svgs" in data 
    # top_sentence_svgs も、内部で amr_to_svg を呼ぶのでスタブ化されたSVGが含まれるはず
    # 例えば、top_sentences が1つだと仮定した場合 (実際はk=3)
    # if data["top_sentence_svgs"]: # 空でないことを確認
    #    first_sentence_key = list(data["top_sentence_svgs"].keys())[0]
    #    assert data["top_sentence_svgs"][first_sentence_key] == "<svg><text>Stubbed AMR SVG</text></svg>"

    assert "consistency_score" in data
    assert data["consistency_score"] == 0.77 # ★スタブされたスコアを期待

    assert "is_consistent" in data
    assert data["is_consistent"] is True # ★スタブされた値を期待

def test_process_amr_bad_input():
    response = client.post("/process_amr", json={"summary": None, "article": "Test article."})
    assert response.status_code == 422