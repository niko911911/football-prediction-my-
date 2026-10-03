import math
from datetime import datetime, timedelta

from .models import Match, MatchStatus, Team

# 基准场均进球（英超经验值），用于实时比分与预测模拟
AVG_HOME_GOALS = 1.36
AVG_AWAY_GOALS = 1.06
MATCH_MINUTES = 90

TEAMS = [
    ("曼城", 1.45, 0.80),
    ("利物浦", 1.40, 0.90),
    ("阿森纳", 1.35, 0.85),
    ("曼联", 1.20, 0.95),
    ("热刺", 1.25, 1.05),
    ("切尔西", 1.10, 1.00),
]

# (主队, 客队, 状态, 距开赛分钟数, 联赛, 轮次)
# 正数=已开赛N分钟前；负数=N分钟后开赛
FIXTURES = [
    ("曼城", "曼联", MatchStatus.LIVE, 62, "英超", "第10轮"),
    ("阿森纳", "利物浦", MatchStatus.LIVE, 48, "英超", "第10轮"),
    ("切尔西", "热刺", MatchStatus.SCHEDULED, -60, "英超", "第10轮"),
    ("利物浦", "曼城", MatchStatus.SCHEDULED, -120, "英超", "第11轮"),
    ("曼联", "阿森纳", MatchStatus.FINISHED, 200, "英超", "第9轮"),
    ("热刺", "切尔西", MatchStatus.FINISHED, 300, "英超", "第9轮"),
]


def current_live_score(
    home_attack: float,
    away_attack: float,
    home_defense: float,
    away_defense: float,
    start_time: datetime,
    now: datetime,
) -> tuple[int, int]:
    """根据已进行时间，按两队强度推算当前比分（用于 live 比赛实时刷新）。"""
    elapsed = (now - start_time).total_seconds() / 60.0
    elapsed = min(max(elapsed, 0.0), MATCH_MINUTES)
    home_rate = (AVG_HOME_GOALS * home_attack / max(away_defense, 0.1)) / MATCH_MINUTES
    away_rate = (AVG_AWAY_GOALS * away_attack / max(home_defense, 0.1)) / MATCH_MINUTES
    return int(math.floor(elapsed * home_rate)), int(math.floor(elapsed * away_rate))


def seed_mock_data(db) -> None:
    """清空并重建模拟数据：球队 + 比赛（含 live/finished 比分与未来赛程）。"""
    db.query(Match).delete()
    db.query(Team).delete()

    teams: dict[str, Team] = {}
    for name, atk, dfn in TEAMS:
        t = Team(name=name, attack=atk, defense=dfn)
        db.add(t)
        db.flush()
        teams[name] = t

    now = datetime.utcnow()
    for home, away, status, mins, league, rnd in FIXTURES:
        start = (
            now - timedelta(minutes=mins)
            if mins >= 0
            else now + timedelta(minutes=-mins)
        )
        h, a = 0, 0
        if status == MatchStatus.FINISHED:
            ht, at = teams[home], teams[away]
            h, a = current_live_score(
                ht.attack, at.attack, ht.defense, at.defense, start, now
            )
        m = Match(
            league=league,
            round=rnd,
            home_team_id=teams[home].id,
            away_team_id=teams[away].id,
            status=status,
            home_score=h,
            away_score=a,
            start_time=start,
        )
        db.add(m)
    db.commit()
