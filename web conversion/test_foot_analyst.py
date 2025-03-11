import json
from google_api import generate
from prompts import FOOT_ANALYST, LOL_DRAFTER_FOCUS
import os
import pandas as pd

def check_coach(team_name, df_coaches):
    coach_name = df_coaches[df_coaches["team_name"] == team_name]["long_name"].values.tolist()
    return coach_name[0] if coach_name else "fifa"

# Load data
df = pd.read_csv('./data/thebest.csv')
df_teams = pd.read_csv('./data/tb_participating_teams.csv')
df_team_coach = pd.read_csv('./data/team_coach.csv')
df["entrenador"] = df.apply(lambda x: check_coach(x.equipo,df_team_coach) if x.entrenador == "fifa" else x.entrenador, axis=1)


if __name__ == "__main__":
    
   # print df as a string without index to a llm
    print()
    tournament_format = """Eliminatoria directa. Enfrentamientos:
    - Arsenal vs FC Barcelona
    - Juventus vs Sporting CP
    - SL Benfica vs Club Brugge
    - FC Bayern München vs Paris Saint Germain"""
    input_text = FOOT_ANALYST.format(list_of_champions=df.to_string(index=False), list_of_teams="[Arsenal, FC Barcelona, Juventus, Sporting CP, SL Benfica, Club Brugge, FC Bayern München, Paris Saint Germain]", tournament_format="Eliminatoria directa. Enfrenatmien")
    generate(input_text, os.getenv("GEMINI_API_KEY"))