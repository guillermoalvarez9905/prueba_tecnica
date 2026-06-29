import logging
import time
from datetime import datetime, timezone

import requests

logger = logging.getLogger(__name__)


class APIExtractor:
    BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"

    def __init__(self):
        self.session = requests.Session()

    def _get(self, endpoint: str, params: dict = None) -> dict:
        url = f"{self.BASE_URL}/{endpoint}"
        for attempt in range(3):
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 429:
                wait = 10 * (attempt + 1)
                logger.warning("Límite de peticiones alcanzado, esperando %ds...", wait)
                time.sleep(wait)
                continue
            response.raise_for_status()
            time.sleep(2)
            return response.json()
        response.raise_for_status()

    def get_all_leagues(self) -> list[dict]:
        data = self._get("all_leagues.php")
        return data.get("leagues") or []

    def get_teams_by_league(self, league: str) -> list[dict]:
        data = self._get("search_all_teams.php", {"l": league})
        return data.get("teams") or []

    def get_players_by_team(self, team_id: str) -> list[dict]:
        data = self._get("lookup_all_players.php", {"id": team_id})
        return data.get("player") or []

    def fetch_players(self) -> list[dict]:
        ingestion_ts = datetime.now(timezone.utc).isoformat()
        leagues = self.get_all_leagues()
        logger.info("Ligas encontradas: %d", len(leagues))

        players = []
        for lg in leagues:
            league_name = lg["strLeague"]
            teams = self.get_teams_by_league(league_name)
            if not teams:
                continue
            logger.info("Liga '%s': %d equipos", league_name, len(teams))
            for team in teams:
                team_players = self.get_players_by_team(team["idTeam"])
                logger.info("  Equipo '%s': %d jugadores", team["strTeam"], len(team_players))
                for p in team_players:
                    players.append({
                        "id_player": p.get("idPlayer"),
                        "str_player": p.get("strPlayer"),
                        "str_nationality": p.get("strNationality"),
                        "str_team": p.get("strTeam"),
                        "str_position": p.get("strPosition"),
                        "date_born": p.get("dateBorn"),
                        "str_sport": p.get("strSport"),
                        "ingestion_timestamp": ingestion_ts,
                    })

        logger.info("Total de jugadores extraídos: %d", len(players))
        return players
