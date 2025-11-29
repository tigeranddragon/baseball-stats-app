# data_fetcher.py
import requests
from bs4 import BeautifulSoup
from models import Team
from typing import List, Optional

class DataFetcher:
    """WebサイトからHTMLを取得するクラス"""
    
    def __init__(self):
        # アクセス拒否を防ぐため、より詳細なブラウザのUser-Agentとヘッダーを設定
        self.headers = {
            # 非常に一般的なWindows ChromeのUser-Agentを設定
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            # 参照元ヘッダーを追加（トップページからの遷移に見せかける）
            'Referer': 'https://npb.jp/', 
            # 受け入れ可能なコンテンツタイプを指定
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        }

    def fetch_html(self, url: str) -> Optional[str]:
        """指定されたURLのHTMLテキストを取得する"""
        try:
            # timeoutも設定
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()  # 4xx, 5xxエラーなら例外発生
            response.encoding = response.apparent_encoding
            return response.text
        except requests.exceptions.RequestException as e:
            # エラー発生時、原因特定のためにステータスコードを表示
            print(f"Error fetching URL {url}: {e}")
            return None
        
class StatsParser:
    """HTMLから成績データを抽出・構造化するクラス"""

    # NPB公式サイトの順位ページ URL
    NPB_STANDINGS_URL = "https://npb.jp/standings/2024/league.html" # 2024年など、確定した年度を指定する

    def parse_team_standings(self, html: str) -> List[Team]:
        """NPB公式サイトの年度別順位表HTMLからチームデータを抽出する"""
        soup = BeautifulSoup(html, 'html.parser')
        teams = []
        
        # NPB公式サイトのHTML構造に基づいて順位表を取得
        # 順位表は usually ID: 'st_c', 'st_p' (セ・リーグ, パ・リーグ)
        
        # セ・リーグとパ・リーグそれぞれのテーブルを探す
        for league_id, league_name in [('st_c', 'Central'), ('st_p', 'Pacific')]:
            table = soup.find('table', id=league_id)
            if not table:
                print(f"Warning: Could not find table for {league_name} league (ID: {league_id}).")
                continue
                
            # データ行の解析 (trタグ)
            rows = table.find_all('tr')
            for row in rows[1:]: # 最初の行はヘッダーなのでスキップ
                cols = row.find_all(['td', 'th'])
                if len(cols) < 8: # 必要な列数があるか確認
                    continue

                try:
                    # cols[0] = 順位, cols[1] = チーム名, ...
                    rank_text = cols[0].get_text(strip=True).replace('位', '') # '1位' -> '1'
                    team_name = cols[1].get_text(strip=True)
                    games = int(cols[2].get_text(strip=True))
                    wins = int(cols[3].get_text(strip=True))
                    losses = int(cols[4].get_text(strip=True))
                    draws = int(cols[5].get_text(strip=True))
                    win_rate_str = cols[6].get_text(strip=True)
                    # 勝率の '-' を 0.0 に変換
                    win_rate = float(win_rate_str) if win_rate_str != '-' else 0.0
                    game_diff = cols[7].get_text(strip=True)

                    team = Team(
                        rank=int(rank_text),
                        name=team_name,
                        games=games,
                        wins=wins,
                        losses=losses,
                        draws=draws,
                        win_rate=win_rate,
                        game_diff=game_diff,
                        league=league_name
                    )
                    teams.append(team)
                except (ValueError, IndexError) as e:
                    print(f"Error parsing row in {league_name}: {e}")
                    continue
        
        return teams

# --- 動作確認用 --- (URLをNPB公式サイトに修正)
if __name__ == "__main__":
    # テスト実行
    fetcher = DataFetcher()
    parser = StatsParser()
    
    # NPB公式サイトの例 (確定データ)
    npb_url = parser.NPB_STANDINGS_URL 
    print(f"Fetching: {npb_url}")

    html = fetcher.fetch_html(npb_url)
    if html:
        teams = parser.parse_team_standings(html)
        print(f"\n取得されたチーム数: {len(teams)}")
        for team in teams:
            print(f"[{team.league}] {team.rank}位: {team.name} (勝率: {team.win_rate})")
    else:
        print("HTMLの取得に失敗しました。")
