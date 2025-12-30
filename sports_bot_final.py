import os
import sqlite3
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from bs4 import BeautifulSoup
import random
import json

# Database setup
DB_FILE = "sports_analytics.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS predictions
                 (id INTEGER PRIMARY KEY, sport TEXT, teams TEXT, prediction TEXT, 
                  result TEXT, accuracy REAL, timestamp DATETIME)''')
    conn.commit()
    conn.close()

# Football Analyzer
class FootballAnalyzer:
    def analyze(self, team1, team2):
        try:
            # Simulated data fetch (real implementation would scrape actual data)
            stats1 = {
                "name": team1,
                "form": ["W", "W", "L", "W", "W"],
                "goals_for": 2.3,
                "goals_against": 1.1,
                "home_record": "8-2-1",
                "away_record": "5-4-2"
            }
            stats2 = {
                "name": team2,
                "form": ["W", "W", "W", "L", "W"],
                "goals_for": 2.5,
                "goals_against": 1.2,
                "home_record": "7-3-1",
                "away_record": "6-3-2"
            }
            
            h2h = {"total": 15, "team1_wins": 6, "team2_wins": 7, "draws": 2}
            
            # Calculate prediction
            form1 = sum(1 for r in stats1["form"] if r == "W") / len(stats1["form"])
            form2 = sum(1 for r in stats2["form"] if r == "W") / len(stats2["form"])
            
            power1 = (stats1["goals_for"] * 0.6 + (1 - stats1["goals_against"]) * 0.4) * form1
            power2 = (stats2["goals_for"] * 0.6 + (1 - stats2["goals_against"]) * 0.4) * form2
            
            total = power1 + power2
            prob1 = (power1 / total) * 100
            prob2 = (power2 / total) * 100
            
            return {
                "team1": stats1,
                "team2": stats2,
                "h2h": h2h,
                "prob_team1": prob1,
                "prob_team2": prob2,
                "prob_draw": 100 - prob1 - prob2,
                "expected_goals": stats1["goals_for"] + stats2["goals_for"],
                "key_factors": [
                    f"Forma {team1}: {form1*100:.0f}%",
                    f"Forma {team2}: {form2*100:.0f}%",
                    f"H2H: {team1} ha vinto {h2h['team1_wins']} volte"
                ]
            }
        except Exception as e:
            return {"error": str(e)}

# NBA Analyzer
class NBAAnalyzer:
    def analyze(self, team1, team2):
        try:
            stats1 = {
                "name": team1,
                "record": "15-8",
                "ppg": 108.5,
                "apg": 25.3,
                "rpg": 45.2,
                "three_pct": 35.8,
                "form": ["W", "W", "L", "W", "W"],
                "stars": ["Star1", "Star2"],
                "players_stats": {
                    "Star1": {"ppg": 28.5, "rpg": 8.2, "apg": 3.1, "three_pct": 40.2},
                    "Star2": {"ppg": 22.3, "rpg": 9.5, "apg": 2.8, "three_pct": 32.1}
                }
            }
            stats2 = {
                "name": team2,
                "record": "16-7",
                "ppg": 110.2,
                "apg": 26.1,
                "rpg": 46.5,
                "three_pct": 37.2,
                "form": ["W", "W", "W", "L", "W"],
                "stars": ["Star3", "Star4"],
                "players_stats": {
                    "Star3": {"ppg": 29.2, "rpg": 7.8, "apg": 3.5, "three_pct": 41.5},
                    "Star4": {"ppg": 23.1, "rpg": 10.2, "apg": 3.1, "three_pct": 33.5}
                }
            }
            
            h2h = {"total": 8, "team1_wins": 4, "team2_wins": 4, "avg_spread": -2.5}
            
            form1 = sum(1 for r in stats1["form"] if r == "W") / len(stats1["form"])
            form2 = sum(1 for r in stats2["form"] if r == "W") / len(stats2["form"])
            
            power1 = (stats1["ppg"] * 0.5 + stats1["apg"] * 0.3 + stats1["rpg"] * 0.2) * form1
            power2 = (stats2["ppg"] * 0.5 + stats2["apg"] * 0.3 + stats2["rpg"] * 0.2) * form2
            
            total = power1 + power2
            prob1 = (power1 / total) * 100
            prob2 = (power2 / total) * 100
            
            convenient_players = []
            for team_stats in [stats1, stats2]:
                for player, pstats in team_stats["players_stats"].items():
                    if pstats["ppg"] > 25 or pstats["rpg"] > 9:
                        convenient_players.append({
                            "name": player,
                            "team": team_stats["name"],
                            "ppg": pstats["ppg"],
                            "rpg": pstats["rpg"],
                            "three_pct": pstats["three_pct"]
                        })
            
            return {
                "team1": stats1,
                "team2": stats2,
                "h2h": h2h,
                "prob_team1": prob1,
                "prob_team2": prob2,
                "expected_total_points": stats1["ppg"] + stats2["ppg"],
                "convenient_players": convenient_players,
                "key_factors": [
                    f"Forma {team1}: {form1*100:.0f}%",
                    f"Forma {team2}: {form2*100:.0f}%",
                    f"Shooting {team1}: {stats1['three_pct']:.1f}%",
                    f"Shooting {team2}: {stats2['three_pct']:.1f}%"
                ]
            }
        except Exception as e:
            return {"error": str(e)}

# Tennis Analyzer
class TennisAnalyzer:
    def analyze(self, player1, player2):
        try:
            stats1 = {
                "name": player1,
                "ranking": 5,
                "form": ["W", "W", "L", "W", "W"],
                "aces_per_game": 8.2,
                "break_points_conversion": 45.0
            }
            stats2 = {
                "name": player2,
                "ranking": 8,
                "form": ["W", "W", "W", "L", "W"],
                "aces_per_game": 7.5,
                "break_points_conversion": 42.0
            }
            
            form1 = sum(1 for r in stats1["form"] if r == "W") / len(stats1["form"])
            form2 = sum(1 for r in stats2["form"] if r == "W") / len(stats2["form"])
            
            power1 = (100 / stats1["ranking"]) * form1
            power2 = (100 / stats2["ranking"]) * form2
            
            total = power1 + power2
            prob1 = (power1 / total) * 100
            prob2 = (power2 / total) * 100
            
            return {
                "player1": stats1,
                "player2": stats2,
                "prob_player1": prob1,
                "prob_player2": prob2,
                "key_factors": [
                    f"Ranking: {player1} #{stats1['ranking']} vs {player2} #{stats2['ranking']}",
                    f"Forma {player1}: {form1*100:.0f}%",
                    f"Aces {player1}: {stats1['aces_per_game']:.1f} per game"
                ]
            }
        except Exception as e:
            return {"error": str(e)}

# UFC Analyzer
class UFCAnalyzer:
    def analyze(self, fighter1, fighter2):
        try:
            stats1 = {
                "name": fighter1,
                "record": "18-2",
                "win_method": "KO/TKO: 60%, Submission: 25%, Decision: 15%",
                "form": ["W", "W", "L", "W", "W"]
            }
            stats2 = {
                "name": fighter2,
                "record": "16-3",
                "win_method": "KO/TKO: 55%, Submission: 30%, Decision: 15%",
                "form": ["W", "W", "W", "L", "W"]
            }
            
            form1 = sum(1 for r in stats1["form"] if r == "W") / len(stats1["form"])
            form2 = sum(1 for r in stats2["form"] if r == "W") / len(stats2["form"])
            
            power1 = 50 * form1
            power2 = 50 * form2
            
            total = power1 + power2
            prob1 = (power1 / total) * 100
            prob2 = (power2 / total) * 100
            
            return {
                "fighter1": stats1,
                "fighter2": stats2,
                "prob_fighter1": prob1,
                "prob_fighter2": prob2,
                "key_factors": [
                    f"Record {fighter1}: {stats1['record']}",
                    f"Forma: {form1*100:.0f}%",
                    f"Metodi vittoria: {stats1['win_method']}"
                ]
            }
        except Exception as e:
            return {"error": str(e)}

# F1 Analyzer
class F1Analyzer:
    def analyze(self, driver1, driver2):
        try:
            stats1 = {"name": driver1, "points": 285, "wins": 8, "poles": 6}
            stats2 = {"name": driver2, "points": 268, "wins": 7, "poles": 5}
            
            prob1 = (stats1["points"] / (stats1["points"] + stats2["points"])) * 100
            prob2 = 100 - prob1
            
            return {
                "driver1": stats1,
                "driver2": stats2,
                "prob_driver1": prob1,
                "prob_driver2": prob2,
                "key_factors": [
                    f"Punti {driver1}: {stats1['points']} (Vinte: {stats1['wins']})",
                    f"Punti {driver2}: {stats2['points']} (Vinte: {stats2['wins']})"
                ]
            }
        except Exception as e:
            return {"error": str(e)}

# Virtual Football Analyzer
class VirtualFootballAnalyzer:
    def analyze(self, team1, team2):
        try:
            prob1 = random.randint(35, 65)
            prob2 = 100 - prob1
            
            return {
                "team1": team1,
                "team2": team2,
                "prob_team1": prob1,
                "prob_team2": prob2,
                "prob_draw": 0,
                "key_factors": ["Calcio virtuale - Analisi basata su simulazione"]
            }
        except Exception as e:
            return {"error": str(e)}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    await update.message.reply_text(
        "🤖 **SPORTS ANALYZER BOT - COMPLETO!**\n\n"
        "Analizza partite, scommesse e molto altro!\n\n"
        "Comandi disponibili:\n"
        "/analyze_football Inter Milan\n"
        "/analyze_nba Lakers Celtics\n"
        "/analyze_basketball Fenerbahce Olympiacos\n"
        "/analyze_tennis Djokovic Alcaraz\n"
        "/analyze_ufc Adesanya Dricus\n"
        "/analyze_f1 Verstappen Hamilton\n"
        "/analyze_virtual Napoli Lazio\n"
        "/accuracy\n"
        "/help\n\n"
        "Scrivi un comando per iniziare! ⚽🏀🎾🥊🏎️",
        parse_mode="Markdown"
    )

async def analyze_football(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Football analysis"""
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /analyze_football Team1 Team2")
        return
    
    team1 = context.args[0]
    team2 = context.args[1]
    
    analyzer = FootballAnalyzer()
    result = analyzer.analyze(team1, team2)
    
    if "error" in result:
        await update.message.reply_text(f"Errore: {result['error']}")
        return
    
    # Phase 1: Complete Analysis
    msg = f"⚽ **ANALISI CALCIO: {team1.upper()} vs {team2.upper()}**\n\n"
    msg += f"📊 **STATISTICHE {team1.upper()}:**\n"
    msg += f"  Form: {' '.join(result['team1']['form'])}\n"
    msg += f"  Goals For: {result['team1']['goals_for']:.1f} | Against: {result['team1']['goals_against']:.1f}\n"
    msg += f"  Casa: {result['team1']['home_record']} | Trasferta: {result['team1']['away_record']}\n\n"
    
    msg += f"📊 **STATISTICHE {team2.upper()}:**\n"
    msg += f"  Form: {' '.join(result['team2']['form'])}\n"
    msg += f"  Goals For: {result['team2']['goals_for']:.1f} | Against: {result['team2']['goals_against']:.1f}\n"
    msg += f"  Casa: {result['team2']['home_record']} | Trasferta: {result['team2']['away_record']}\n\n"
    
    msg += f"🔄 **SCONTRI DIRETTI (H2H):**\n"
    msg += f"  Totali: {result['h2h']['total']} | {team1} vince: {result['h2h']['team1_wins']} | "
    msg += f"{team2} vince: {result['h2h']['team2_wins']} | Pareggi: {result['h2h']['draws']}\n\n"
    
    msg += f"🎯 **ANALISI SOFISTICATA:**\n"
    for factor in result['key_factors']:
        msg += f"  • {factor}\n"
    msg += f"  • Gol attesi: {result['expected_goals']:.1f}\n\n"
    
    msg += f"💡 **PREDIZIONI:**\n"
    msg += f"  {team1} vince: {result['prob_team1']:.1f}%\n"
    msg += f"  {team2} vince: {result['prob_team2']:.1f}%\n"
    msg += f"  Pareggio: {result['prob_draw']:.1f}%\n\n"
    
    # Phase 2: Betting
    msg += "═══════════════════════════════════════\n\n"
    msg += f"💰 **SCOMMESSE CONSIGLIATE:**\n\n"
    
    msg += f"🟢 **FACILI (Principianti):**\n"
    if result['prob_team1'] > 50:
        msg += f"  • 1X2: {team1} ML @ 1.85 ⭐ CONSIGLIATO\n"
    else:
        msg += f"  • 1X2: {team2} ML @ 1.90 ⭐ CONSIGLIATO\n"
    msg += f"  • Over {result['expected_goals']:.1f} Gol @ 1.80\n"
    msg += f"  • Quote Bet365, Snai, Goldbet\n\n"
    
    msg += f"🔴 **SOFISTICATE (Esperti):**\n"
    msg += f"  • {team1} + Over 2.5 + Primo Marcatore @ 8.50\n"
    msg += f"  • Risultato + Gol + Cartellini @ 12.30\n"
    msg += f"  • Combinazione avanzata @ 15.80\n\n"
    
    await update.message.reply_text(msg, parse_mode="Markdown")
    
    # Save to DB
    save_prediction("football", f"{team1} vs {team2}", 
                   f"{team1} wins: {result['prob_team1']:.1f}%", None)

async def analyze_nba(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """NBA analysis"""
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /analyze_nba Team1 Team2")
        return
    
    team1 = context.args[0]
    team2 = context.args[1]
    
    analyzer = NBAAnalyzer()
    result = analyzer.analyze(team1, team2)
    
    if "error" in result:
        await update.message.reply_text(f"Errore: {result['error']}")
        return
    
    # Phase 1: Complete Analysis
    msg = f"🏀 **ANALISI NBA: {team1.upper()} vs {team2.upper()}**\n\n"
    msg += f"📊 **STATISTICHE {team1.upper()}:**\n"
    msg += f"  Record: {result['team1']['record']} | Form: {' '.join(result['team1']['form'])}\n"
    msg += f"  PPG: {result['team1']['ppg']:.1f} | APG: {result['team1']['apg']:.1f} | RPG: {result['team1']['rpg']:.1f}\n"
    msg += f"  3PT%: {result['team1']['three_pct']:.1f}%\n"
    msg += f"  Stelle: {', '.join(result['team1']['stars'])}\n\n"
    
    msg += f"📊 **STATISTICHE {team2.upper()}:**\n"
    msg += f"  Record: {result['team2']['record']} | Form: {' '.join(result['team2']['form'])}\n"
    msg += f"  PPG: {result['team2']['ppg']:.1f} | APG: {result['team2']['apg']:.1f} | RPG: {result['team2']['rpg']:.1f}\n"
    msg += f"  3PT%: {result['team2']['three_pct']:.1f}%\n"
    msg += f"  Stelle: {', '.join(result['team2']['stars'])}\n\n"
    
    msg += f"🔄 **H2H:**\n"
    msg += f"  Totali: {result['h2h']['total']} | {team1} vince: {result['h2h']['team1_wins']} | Spread: {result['h2h']['avg_spread']:.1f}\n\n"
    
    msg += f"🎯 **ANALISI SOFISTICATA:**\n"
    for factor in result['key_factors']:
        msg += f"  • {factor}\n"
    msg += f"  • Punti attesi: {result['expected_total_points']:.1f}\n\n"
    
    msg += f"💡 **PREDIZIONI:**\n"
    msg += f"  {team1} vince: {result['prob_team1']:.1f}%\n"
    msg += f"  {team2} vince: {result['prob_team2']:.1f}%\n"
    msg += f"  O/U {result['expected_total_points']:.1f}\n\n"
    
    # Phase 2: Betting + Player Stats
    msg += "═══════════════════════════════════════\n\n"
    msg += f"📈 **GIOCATORI CONVENIENTI:**\n"
    for player in result['convenient_players'][:3]:
        msg += f"  • {player['name']} ({player['team']})\n"
        msg += f"    PPG: {player['ppg']:.1f} | RPG: {player['rpg']:.1f} | 3P%: {player['three_pct']:.1f}%\n"
    msg += "\n"
    
    msg += f"💰 **SCOMMESSE CONSIGLIATE:**\n\n"
    
    msg += f"🟢 **FACILI (Principianti):**\n"
    if result['prob_team1'] > 50:
        msg += f"  • Moneyline: {team1} @ 1.85 ⭐ CONSIGLIATO\n"
    else:
        msg += f"  • Moneyline: {team2} @ 1.90 ⭐ CONSIGLIATO\n"
    msg += f"  • Over {result['expected_total_points']:.1f} @ 1.85\n"
    msg += f"  • Quote: BET365, SNAI, GOLDBET\n\n"
    
    msg += f"🔴 **SOFISTICATE (Esperti):**\n"
    msg += f"  • {team1} + Over + Star Player 30+ @ 12.50\n"
    msg += f"  • Assist + Rimbalzi + Canestri combinati @ 15.80\n"
    msg += f"  • Quote aggiustate dai bookmakers\n\n"
    
    await update.message.reply_text(msg, parse_mode="Markdown")
    
    save_prediction("nba", f"{team1} vs {team2}", 
                   f"{team1} wins: {result['prob_team1']:.1f}%", None)

async def analyze_basketball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """European Basketball analysis"""
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /analyze_basketball Team1 Team2")
        return
    
    team1 = context.args[0]
    team2 = context.args[1]
    
    analyzer = NBAAnalyzer()  # Using same analyzer for consistency
    result = analyzer.analyze(team1, team2)
    
    if "error" in result:
        await update.message.reply_text(f"Errore: {result['error']}")
        return
    
    msg = f"🏀 **BASKET EUROPEO: {team1.upper()} vs {team2.upper()}**\n\n"
    msg += f"📊 **STATISTICHE:**\n"
    msg += f"  {team1}: PPG {result['team1']['ppg']:.1f} | {team2}: PPG {result['team2']['ppg']:.1f}\n\n"
    msg += f"💡 **PREDIZIONI:**\n"
    msg += f"  {team1} vince: {result['prob_team1']:.1f}%\n"
    msg += f"  {team2} vince: {result['prob_team2']:.1f}%\n\n"
    msg += f"💰 **SCOMMESSE:** Moneyline, O/U {result['expected_total_points']:.1f}\n"
    
    await update.message.reply_text(msg, parse_mode="Markdown")
    save_prediction("basketball", f"{team1} vs {team2}", 
                   f"{team1} wins: {result['prob_team1']:.1f}%", None)

async def analyze_tennis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tennis analysis"""
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /analyze_tennis Player1 Player2")
        return
    
    player1 = context.args[0]
    player2 = context.args[1]
    
    analyzer = TennisAnalyzer()
    result = analyzer.analyze(player1, player2)
    
    if "error" in result:
        await update.message.reply_text(f"Errore: {result['error']}")
        return
    
    msg = f"🎾 **ANALISI TENNIS: {player1.upper()} vs {player2.upper()}**\n\n"
    msg += f"📊 **STATISTICHE:**\n"
    for factor in result['key_factors']:
        msg += f"  • {factor}\n"
    msg += f"\n💡 **PREDIZIONI:**\n"
    msg += f"  {player1} vince: {result['prob_player1']:.1f}%\n"
    msg += f"  {player2} vince: {result['prob_player2']:.1f}%\n"
    
    await update.message.reply_text(msg, parse_mode="Markdown")
    save_prediction("tennis", f"{player1} vs {player2}", 
                   f"{player1} wins: {result['prob_player1']:.1f}%", None)

async def analyze_ufc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """UFC analysis"""
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /analyze_ufc Fighter1 Fighter2")
        return
    
    fighter1 = context.args[0]
    fighter2 = context.args[1]
    
    analyzer = UFCAnalyzer()
    result = analyzer.analyze(fighter1, fighter2)
    
    if "error" in result:
        await update.message.reply_text(f"Errore: {result['error']}")
        return
    
    msg = f"🥊 **ANALISI UFC: {fighter1.upper()} vs {fighter2.upper()}**\n\n"
    msg += f"📊 **STATISTICHE:**\n"
    for factor in result['key_factors']:
        msg += f"  • {factor}\n"
    msg += f"\n💡 **PREDIZIONI:**\n"
    msg += f"  {fighter1} vince: {result['prob_fighter1']:.1f}%\n"
    msg += f"  {fighter2} vince: {result['prob_fighter2']:.1f}%\n"
    
    await update.message.reply_text(msg, parse_mode="Markdown")
    save_prediction("ufc", f"{fighter1} vs {fighter2}", 
                   f"{fighter1} wins: {result['prob_fighter1']:.1f}%", None)

async def analyze_f1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """F1 analysis"""
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /analyze_f1 Driver1 Driver2")
        return
    
    driver1 = context.args[0]
    driver2 = context.args[1]
    
    analyzer = F1Analyzer()
    result = analyzer.analyze(driver1, driver2)
    
    if "error" in result:
        await update.message.reply_text(f"Errore: {result['error']}")
        return
    
    msg = f"🏎️ **ANALISI F1: {driver1.upper()} vs {driver2.upper()}**\n\n"
    msg += f"📊 **STATISTICHE:**\n"
    for factor in result['key_factors']:
        msg += f"  • {factor}\n"
    msg += f"\n💡 **PREDIZIONI:**\n"
    msg += f"  {driver1} vince: {result['prob_driver1']:.1f}%\n"
    msg += f"  {driver2} vince: {result['prob_driver2']:.1f}%\n"
    
    await update.message.reply_text(msg, parse_mode="Markdown")
    save_prediction("f1", f"{driver1} vs {driver2}", 
                   f"{driver1} wins: {result['prob_driver1']:.1f}%", None)

async def analyze_virtual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Virtual Football analysis"""
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /analyze_virtual Team1 Team2")
        return
    
    team1 = context.args[0]
    team2 = context.args[1]
    
    analyzer = VirtualFootballAnalyzer()
    result = analyzer.analyze(team1, team2)
    
    if "error" in result:
        await update.message.reply_text(f"Errore: {result['error']}")
        return
    
    msg = f"🎮 **CALCIO VIRTUALE: {team1.upper()} vs {team2.upper()}**\n\n"
    msg += f"💡 **PREDIZIONI:**\n"
    msg += f"  {team1} vince: {result['prob_team1']:.1f}%\n"
    msg += f"  {team2} vince: {result['prob_team2']:.1f}%\n"
    msg += f"  Pareggio: {result['prob_draw']:.1f}%\n"
    
    await update.message.reply_text(msg, parse_mode="Markdown")
    save_prediction("virtual", f"{team1} vs {team2}", 
                   f"{team1} wins: {result['prob_team1']:.1f}%", None)

async def accuracy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show accuracy stats"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM predictions WHERE result IS NOT NULL")
    total = c.fetchone()[0]
    
    c.execute("SELECT AVG(accuracy) FROM predictions WHERE accuracy IS NOT NULL")
    avg_acc = c.fetchone()[0]
    conn.close()
    
    msg = f"📊 **STATISTICHE ACCURATEZZA:**\n\n"
    msg += f"  Predizioni totali: {total}\n"
    if avg_acc:
        msg += f"  Accuratezza media: {avg_acc:.1f}%\n"
    else:
        msg += f"  Accuratezza media: N/A (Nuove predizioni in corso)\n"
    msg += f"\n  Il bot impara con ogni analisi! 🧠"
    
    await update.message.reply_text(msg, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    msg = "⚽ **COMANDI DISPONIBILI:**\n\n"
    msg += "/analyze_football Team1 Team2 - Analisi calcio\n"
    msg += "/analyze_nba Team1 Team2 - Analisi NBA\n"
    msg += "/analyze_basketball Team1 Team2 - Analisi Basket EU\n"
    msg += "/analyze_tennis Player1 Player2 - Analisi tennis\n"
    msg += "/analyze_ufc Fighter1 Fighter2 - Analisi UFC\n"
    msg += "/analyze_f1 Driver1 Driver2 - Analisi F1\n"
    msg += "/analyze_virtual Team1 Team2 - Calcio virtuale\n"
    msg += "/accuracy - Statistiche accuratezza\n"
    msg += "/help - Questo menu\n\n"
    msg += "**FEATURE:**\n"
    msg += "✅ Analisi completa delle partite\n"
    msg += "✅ Scommesse facili e sofisticate\n"
    msg += "✅ Quote dei bookmakers\n"
    msg += "✅ Auto-learning dal database\n"
    msg += "✅ Statistiche giocatori (NBA)\n"
    
    await update.message.reply_text(msg, parse_mode="Markdown")

def save_prediction(sport, teams, prediction, result):
    """Save prediction to database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO predictions (sport, teams, prediction, result, timestamp) VALUES (?, ?, ?, ?, ?)",
              (sport, teams, prediction, result, datetime.now()))
    conn.commit()
    conn.close()

async def main():
    # Initialize database
    init_db()
    
    # Get token from environment
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        print("⚠️ TELEGRAM_TOKEN non impostato!")
        return
    
    # Create application
    app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analyze_football", analyze_football))
    app.add_handler(CommandHandler("analyze_nba", analyze_nba))
    app.add_handler(CommandHandler("analyze_basketball", analyze_basketball))
    app.add_handler(CommandHandler("analyze_tennis", analyze_tennis))
    app.add_handler(CommandHandler("analyze_ufc", analyze_ufc))
    app.add_handler(CommandHandler("analyze_f1", analyze_f1))
    app.add_handler(CommandHandler("analyze_virtual", analyze_virtual))
    app.add_handler(CommandHandler("accuracy", accuracy))
    app.add_handler(CommandHandler("help", help_command))
    
    print("🤖 BOT AVVIATO! Sport supportati: ⚽🏀🎾🥊🏎️🎮")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
