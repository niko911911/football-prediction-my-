from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Match, MatchStatus
from ..mock_data import current_live_score
from ..prediction import predict_match
from ..schemas import MatchOut, PredictionOut, TeamOut

router = APIRouter(prefix="/api/matches", tags=["matches"])


def _match_out(match: Match) -> MatchOut:
    """序列化比赛；live 比赛按当前时间实时推算比分。"""
    now = datetime.utcnow()
    home_score, away_score = match.home_score, match.away_score
    if match.status == MatchStatus.LIVE and match.home_team and match.away_team:
        home_score, away_score = current_live_score(
            match.home_team.attack,
            match.away_team.attack,
            match.home_team.defense,
            match.away_team.defense,
            match.start_time,
            now,
        )
    return MatchOut(
        id=match.id,
        league=match.league,
        round=match.round,
        home_team=TeamOut.model_validate(match.home_team),
        away_team=TeamOut.model_validate(match.away_team),
        status=match.status,
        home_score=home_score,
        away_score=away_score,
        start_time=match.start_time,
        updated_at=match.updated_at,
    )


@router.get("", response_model=List[MatchOut])
def list_matches(
    date: str = None,
    league: str = None,
    db: Session = Depends(get_db),
):
    q = db.query(Match)
    if league:
        q = q.filter(Match.league == league)
    if date:
        q = q.filter(func.date(Match.start_time) == date)
    matches = q.order_by(Match.start_time).all()
    return [_match_out(m) for m in matches]


@router.get("/{match_id}", response_model=MatchOut)
def get_match(match_id: int, db: Session = Depends(get_db)):
    match = db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="match not found")
    return _match_out(match)


@router.get("/{match_id}/prediction", response_model=PredictionOut)
def match_prediction(match_id: int, db: Session = Depends(get_db)):
    match = db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="match not found")
    if not match.home_team or not match.away_team:
        raise HTTPException(status_code=400, detail="team data missing")
    pred = predict_match(match, match.home_team, match.away_team)
    return PredictionOut.model_validate(pred)
