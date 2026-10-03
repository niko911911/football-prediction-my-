import os
import sys
import tempfile

# 必须在导入 app 之前设置测试数据库，避免污染项目中的 app.db
_TMP = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = "sqlite:///" + _TMP.name.replace("\\", "/")
os.environ["USE_MOCK_DATA"] = "true"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app


def test_health():
    with TestClient(app) as client:
        r = client.get("/api/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert body["mock_data"] is True


def test_prediction_ok():
    with TestClient(app) as client:
        r = client.get("/api/matches/1/prediction")
        assert r.status_code == 200
        data = r.json()
        total = data["home_win_prob"] + data["draw_prob"] + data["away_win_prob"]
        assert abs(total - 1.0) < 1e-3
        assert len(data["top_scores"]) == 3
        assert all(0 <= s["home"] <= 12 and 0 <= s["away"] <= 12 for s in data["top_scores"])


def test_prediction_404():
    with TestClient(app) as client:
        r = client.get("/api/matches/9999/prediction")
        assert r.status_code == 404
