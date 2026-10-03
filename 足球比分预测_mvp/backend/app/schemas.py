from datetime import datetime
from typing import List

from pydantic import BaseModel

from .models import MatchStatus


class TeamOut(BaseModel):
    id: int
    name: str
    attack: float
    defense: float

    model_config = {"from_attributes": True}


class MatchOut(BaseModel):
    id: int
    league: str
    round: str
    home_team: TeamOut
    away_team: TeamOut
    status: MatchStatus
    home_score: int
    away_score: int
    start_time: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ScoreProbOut(BaseModel):
    home: int
    away: int
    probability: float

    model_config = {"from_attributes": True}


class PredictionOut(BaseModel):
    match_id: int
    home_team: str
    away_team: str
    expected_home_goals: float
    expected_away_goals: float
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    top_scores: List[ScoreProbOut]
    status: str

    model_config = {"from_attributes": True}
