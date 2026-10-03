import math
from dataclasses import dataclass
from typing import List

from .models import Match, Team

# 联赛基准场均进球（英超经验值）
AVG_HOME_GOALS = 1.36
AVG_AWAY_GOALS = 1.06
# 比分联合分布计算上限（双方进球数 0..MAX_GOALS）
MAX_GOALS = 12


@dataclass
class ScoreProb:
    home: int
    away: int
    probability: float


@dataclass
class Prediction:
    match_id: int
    home_team: str
    away_team: str
    expected_home_goals: float
    expected_away_goals: float
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    top_scores: List[ScoreProb]
    status: str


def poisson_pmf(k: int, lam: float) -> float:
    """泊松分布概率质量函数，使用 lgamma 保证数值稳定。"""
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(-lam + k * math.log(lam) - math.lgamma(k + 1))


def predict_match(match: Match, home: Team, away: Team) -> Prediction:
    """基于 Poisson 分布预测比分。

    lambda_home = 基准主队场均 * 主队攻击力 * 客队防守力
    lambda_away = 基准客队场均 * 客队攻击力 * 主队防守力
    双方进球相互独立，比分概率 = P_home(i) * P_away(j)。
    """
    lam_h = AVG_HOME_GOALS * home.attack * away.defense
    lam_a = AVG_AWAY_GOALS * away.attack * home.defense

    grid = []
    for i in range(MAX_GOALS + 1):
        for j in range(MAX_GOALS + 1):
            p = poisson_pmf(i, lam_h) * poisson_pmf(j, lam_a)
            grid.append((i, j, p))

    home_win = sum(p for i, j, p in grid if i > j)
    draw = sum(p for i, j, p in grid if i == j)
    away_win = sum(p for i, j, p in grid if i < j)

    ranked = sorted(grid, key=lambda x: x[2], reverse=True)
    top = [ScoreProb(h, a, round(p, 4)) for (h, a, p) in ranked[:3]]

    return Prediction(
        match_id=match.id,
        home_team=home.name,
        away_team=away.name,
        expected_home_goals=round(lam_h, 3),
        expected_away_goals=round(lam_a, 3),
        home_win_prob=round(home_win, 4),
        draw_prob=round(draw, 4),
        away_win_prob=round(away_win, 4),
        top_scores=top,
        status=match.status.value,
    )
