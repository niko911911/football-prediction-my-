import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Match, MatchStatus, Team
from app.prediction import poisson_pmf, predict_match


def make_match():
    home = Team(id=1, name="曼城", attack=1.45, defense=0.80)
    away = Team(id=2, name="切尔西", attack=1.10, defense=1.00)
    match = Match(id=1, status=MatchStatus.SCHEDULED, home_team_id=1, away_team_id=2)
    match.home_team = home
    match.away_team = away
    return match, home, away


def test_prob_sum():
    match, home, away = make_match()
    pred = predict_match(match, home, away)
    total = pred.home_win_prob + pred.draw_prob + pred.away_win_prob
    assert abs(total - 1.0) < 1e-3, f"主胜+平+客胜概率和应≈1，实际 {total}"


def test_top3_format():
    match, home, away = make_match()
    pred = predict_match(match, home, away)
    assert len(pred.top_scores) == 3
    prev = 1.0
    for s in pred.top_scores:
        assert isinstance(s.home, int) and isinstance(s.away, int)
        assert 0 <= s.home <= 12 and 0 <= s.away <= 12
        assert s.probability <= prev + 1e-9
        prev = s.probability


def test_poisson_pmf():
    total = sum(poisson_pmf(k, 1.5) for k in range(0, 40))
    assert abs(total - 1.0) < 1e-6


if __name__ == "__main__":
    test_prob_sum()
    test_top3_format()
    test_poisson_pmf()
    print("ALL_TESTS_PASSED")
