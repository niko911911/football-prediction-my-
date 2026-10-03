# 足球比分预测应用（MVP）

基于 **Poisson 分布** 的足球比分概率预测全栈应用。可在 `USE_MOCK_DATA=true` 下无密钥直接运行。

## 技术栈
- 后端：Python 3.11+ / FastAPI / SQLAlchemy 2.x / SQLite
- 前端：单页 HTML + 原生 JS + Tailwind CSS（CDN）
- 预测：Poisson 分布（独立攻击力/防守力参数）
- 部署：Docker（阶段 5 提供，含 Dockerfile / docker-compose.yml）

## 功能
1. 比赛列表、比赛详情
2. 主胜 / 平 / 客胜概率
3. Top3 最可能比分
4. 模拟数据模式（`USE_MOCK_DATA=true` 无密钥可跑）
5. 前端每 5 秒轮询刷新比分与预测

## 目录结构（最终）
```
足球比分预测/
├── README.md                  # 项目文档与运行指南
├── .env.example               # 环境变量模板
├── .gitignore
├── .dockerignore
├── Dockerfile                 # 后端+前端一体镜像
├── docker-compose.yml         # 一键启动
├── backend/
│   ├── requirements.txt       # 依赖清单（无版本锁定）
│   └── app/
│       ├── __init__.py
│       ├── main.py            # FastAPI 实例 + CORS + 静态托管 + 路由
│       ├── config.py          # 环境变量集中校验
│       ├── database.py        # SQLAlchemy 引擎/会话
│       ├── models.py          # ORM 模型（Team / Match）
│       ├── schemas.py         # Pydantic 响应模型
│       ├── mock_data.py       # 模拟种子数据 + 实时比分
│       ├── prediction.py      # Poisson 预测引擎
│       └── routers/
│           ├── __init__.py
│           └── matches.py     # /api/matches 列表/详情/预测
│   └── tests/
│       ├── test_prediction.py # 预测引擎单元测试
│       └── test_api.py        # API 测试（health / prediction）
└── frontend/
    └── index.html             # SPA 页面（Tailwind CDN）
```

## 环境变量（.env）
| 变量 | 默认 | 说明 |
|------|------|------|
| `PORT` | `8000` | 后端监听端口 |
| `USE_MOCK_DATA` | `true` | `true` 时使用内置模拟数据，无需任何外部密钥 |
| `DATABASE_URL` | `sqlite:///./app.db` | SQLite 连接串（相对 backend 目录） |
| `CORS_ORIGINS` | `http://localhost:8000` | 允许跨域来源，逗号分隔；生产改为具体域名 |

## 安装与运行（常见问题）
- **依赖未固定版本**：`requirements.txt` 已去除 `==` 固定版本（并去掉 `uvicorn[standard]` 的 extra），由 pip 自动匹配当前 Python；已在 Python 3.14 验证可用。
- **镜像问题**：本机 pip 默认指向 `pypi.tuna.tsinghua.edu.cn` 镜像，该镜像当前返回空（表现为 `from versions: none`）。遇此问题请改用官方源：
  `pip install -i https://pypi.org/simple -r requirements.txt`
- 启动：`cd backend && python -m app.main`，健康检查 `curl http://localhost:8000/api/health`。

## 本地运行指南（Windows，基于实际环境）
本机环境：Python 3.14 安装在 `E:\deve\python\python.exe`（注意是 **deve**，不是 dev；`C:\Users\zyd66\AppData\Local\Programs\Python\Python314\...` 在本机不存在）。

```bash
# 1) 安装依赖（本机 pip 默认清华镜像异常，改用官方源）
cd C:\Users\zyd66\Desktop\足球比分预测\backend
E:\deve\python\python.exe -m pip install -i https://pypi.org/simple -r requirements.txt

# 2) 启动服务（监听 8000）
E:\deve\python\python.exe -m app.main

# 3) 验证
curl http://localhost:8000/api/health        # -> {"status":"ok","mock_data":true}
start http://localhost:8000/                  # 浏览器打开前端页面
```

可选：跑测试（需先装 pytest 与 httpx）：
```bash
E:\deve\python\python.exe -m pip install -i https://pypi.org/simple pytest httpx
E:\deve\python\python.exe -m pytest tests/ -q
```

## Docker 运行指南
```bash
# 构建并一键启动（后端 API + 前端静态页 同容器）
docker-compose up --build
start http://localhost:8000/
```
说明：镜像基于 `python:3.12-slim`；`docker-compose.yml` 的 `build: .` 以项目根为构建上下文；`.dockerignore` 已忽略 `.git`、`__pycache__`、`*.db`、`.env` 等。

## 阶段 5 验收命令与预期结果
```bash
cd 足球比分预测/backend
E:\deve\python\python.exe -m pip install -i https://pypi.org/simple pytest httpx
E:\deve\python\python.exe -m pytest tests/ -q
```
预期：pytest 退出码 0，全部通过（`test_health`、`test_prediction_ok`、`test_prediction_404`、`test_prob_sum`、`test_top3_format`、`test_poisson_pmf`）。

Docker 验收（需本机已安装 Docker）：
```bash
cd 足球比分预测
docker-compose up --build
curl http://localhost:8000/api/health   # -> {"status":"ok","mock_data":true}
```
预期：`docker-compose up --build` 成功构建镜像并启动容器，浏览器打开 `http://localhost:8000/` 与本地运行效果一致。

## 关键假设（信息不足时的合理默认值）
1. **接口前缀**：REST API 统一挂在 `/api` 下；前端 `index.html` 由 FastAPI 通过 `StaticFiles` 托管在根路径 `/`，默认同域访问，规避跨域；同时保留 `CORS_ORIGINS` 以支持前后端分离部署。
2. **模拟数据**：内置 6 支球队与若干比赛；比赛含 `status`（scheduled/live/finished）与 `home_score`/`away_score` 实时比分字段。模拟模式下比分会随轮询"自然推进"，以便演示 5 秒刷新效果。
3. **Poisson 参数**：预测使用两队攻击力/防守力强度，基准场均进球参考英超经验值（主场约 1.36，客场约 1.06），强度系数来自模拟数据或经验均值。
4. **概率计算**：主胜/平/客胜由比分联合分布求和得到；Top3 比分为联合概率最高的三个 (home, away) 组合。
5. **实时性**：前端每 5 秒轮询 `/api/matches` 与 `/api/matches/{id}` 获取最新比分与预测。

## 数据模型（阶段 2）
- **Team**：`id, name(唯一), attack(攻击力系数), defense(防守力系数)`
- **Match**：`id, league, round, home_team_id, away_team_id, status(scheduled/live/finished), home_score, away_score, start_time, updated_at`
- **实时比分模拟**：`mock_data.current_live_score()` 依据已进行分钟数与两队强度，按基准场均进球（主 1.36 / 客 1.06）推算当前比分，用于 live 比赛随轮询推进；finished 比赛落地最终比分，scheduled 比赛为 0-0。
- **启动播种**：`USE_MOCK_DATA=true` 时，`lifespan` 在 `create_all` 后调用 `seed_mock_data()`，清空并重建 6 队 + 6 场比赛（2 live / 2 scheduled / 2 finished）。
- **健康检查**：`GET /api/health` 返回 `{"status":"ok","mock_data":true}`。

## 预测引擎（阶段 3）
- `prediction.py`：`poisson_pmf(k, lam)` 用 `lgamma` 保证数值稳定；`predict_match()` 计算
  `lambda_home = 1.36 * 主队攻击 * 客队防守`、`lambda_away = 1.06 * 客队攻击 * 主队防守`，
  枚举 0..12 比分联合分布，输出主胜/平/客胜概率与 Top3 最可能比分（含双方预期进球数）。
- 接口：`GET /api/matches/{id}/prediction` 返回 `PredictionOut`（已在 `main.py` 接入路由）。
- 测试：`tests/test_prediction.py` 验证预测引擎（概率和≈1、Top3 格式、`poisson_pmf` 归一化）；`tests/test_api.py`（pytest + TestClient）覆盖 `GET /api/health` 与 `GET /api/matches/{id}/prediction`（含 404）。

## 阶段交付计划
- 阶段 1：项目结构与 README（本阶段）
- 阶段 2：后端 ORM 模型与模拟数据
- 阶段 3：Poisson 预测引擎
- 阶段 4：REST API（列表/详情/预测）+ 前端单页（Tailwind + 5 秒刷新）
- 阶段 5：收尾——pytest 测试、Docker 化、README 与清理（本阶段）

## 阶段 1 验收命令与预期结果
```bash
cd 足球比分预测
ls -R
```
预期：存在 `README.md`、`.env.example`、`.gitignore`、`backend/requirements.txt`、`backend/app/__init__.py`、`backend/app/routers/__init__.py`，目录结构与上方一致。

## 阶段 2 验收命令与预期结果
```bash
cd 足球比分预测/backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```
启动后另开终端：
```bash
curl http://localhost:8000/api/health
```
预期：返回 `{"status":"ok","mock_data":true}`，且 `backend/app.db` 已生成（含 teams / matches 表与模拟数据）。

## 阶段 3 验收命令与预期结果
```bash
cd 足球比分预测/backend
# 依赖安装（阶段 2 已完成可跳过）
pip install -r requirements.txt
# 运行单元测试
python tests/test_prediction.py
# 启动后请求预测接口（先取一个存在的 match id，例如 1）
python -m app.main &
curl http://localhost:8000/api/matches/1/prediction
```
单元测试预期：打印 `ALL_TESTS_PASSED`。
接口预期：返回 JSON 含 `home_win_prob`、`draw_prob`、`away_win_prob`（三者之和≈1）、`expected_home_goals`、`expected_away_goals`、`top_scores`（3 个元素，如 `[{"home":2,"away":1,...},...]`）。
不存在的 id 返回 404。

## 阶段 4 验收命令与预期结果
```bash
cd 足球比分预测/backend
E:/deve/python/python.exe -m app.main &
# 比赛列表（按今日日期 / 联赛过滤）
curl "http://localhost:8000/api/matches?date=2026-10-03"
curl "http://localhost:8000/api/matches?league=英超"
# 比赛详情
curl http://localhost:8000/api/matches/1
# 预测（阶段 3 已测）
curl http://localhost:8000/api/matches/1/prediction
```
预期：
- `GET /api/matches` 返回数组，每项含嵌套 `home_team`/`away_team` 与 `home_score`/`away_score`；`live` 比赛比分为实时推算值（随轮询变化）。
- `GET /api/matches?league=英超` 仅返回英超比赛；`?date=YYYY-MM-DD` 按 UTC 日期过滤。
- `GET /api/matches/{id}` 返回单场详情；不存在返回 404。
- 浏览器打开 `http://localhost:8000/`（FastAPI 静态托管 `frontend/index.html`）可见比赛列表，点击查看详情/预测，每 5 秒自动刷新比分与概率。
