# models.py
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class Team:
    """チームの順位情報を保持するデータクラス"""
    rank: int
    name: str
    games: int
    wins: int
    losses: int
    draws: int
    win_rate: float
    game_diff: str  # ゲーム差は "1.5" や "-" (首位) の場合があるため文字列
    league: str     # "Central" or "Pacific"

@dataclass
class PlayerStats:
    """選手の個人成績を保持するデータクラス"""
    rank: int
    name: str
    team: str
    data: Dict[str, Any]  # 成績の詳細（打率、本塁打など変動するため辞書で持つ）
    stat_type: str        # "batter" or "pitcher"
