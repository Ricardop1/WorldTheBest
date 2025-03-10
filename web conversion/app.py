from flask import Flask, render_template, jsonify, request, url_for
import pandas as pd
import json
import random
import os

app = Flask(__name__, static_url_path='/static')


def check_coach(team_name, df_coaches):
    coach_name = df_coaches[df_coaches["team_name"] == team_name]["long_name"].values.tolist()
    return coach_name[0] if coach_name else "fifa"

def prepare_cumulative_victories(dataframe):
    # Ensure all editions and coaches are represented
    all_editions = dataframe['edicion'].unique()
    all_coaches = dataframe['entrenador'].unique()

    # Create a full grid of editions x coaches
    full_grid = pd.DataFrame([(edition, coach) for edition in all_editions for coach in all_coaches],
                             columns=['edicion', 'entrenador'])

    # Merge with actual victories data
    victories = dataframe.groupby(['edicion', 'entrenador']).size().reset_index(name='victories')
    merged = full_grid.merge(victories, on=['edicion', 'entrenador'], how='left').fillna(0)

    # Calculate cumulative victories
    merged['victories'] = merged['victories'].astype(int)
    merged['cumulative_victories'] = merged.groupby('entrenador')['victories'].cumsum()

    return merged

# Load data
df = pd.read_csv('./data/thebest.csv')
df_teams = pd.read_csv('./data/tb_participating_teams.csv')
df_team_coach = pd.read_csv('./data/team_coach.csv')
df["entrenador"] = df.apply(lambda x: check_coach(x.equipo,df_team_coach) if x.entrenador == "fifa" else x.entrenador, axis=1)
# Add cumulative victories column
df["cumulative_victories"] = df.groupby("entrenador").cumcount() + 1


@app.route('/')
def index():
    # Prepare data for tables
    equipo_counts = df['equipo'].value_counts().reset_index()
    equipo_counts.columns = ['equipo', 'victories']

    entrenador_counts = df['entrenador'].value_counts().reset_index()
    entrenador_counts.columns = ['entrenador', 'victories']

    # Prepare timeline data
    timeline_data = df[['edicion', 'equipo']].sort_values('edicion').to_dict(orient='records')

    # Prepare cumulative victories with fixed data
    cumulative_victories = prepare_cumulative_victories(df)

    # Prepare data for participating teams panel
    teams_by_league = df_teams.groupby('league')['team_name'].apply(list).to_dict()
    filter_coaches = entrenador_counts[entrenador_counts["victories"] >= 3]["entrenador"].values.tolist()

    return render_template(
        'index.html',
        equipo_counts=equipo_counts.to_dict(orient='records'),
        entrenador_counts=entrenador_counts.to_dict(orient='records'),
        cumulative_victories=cumulative_victories[cumulative_victories["entrenador"].isin(filter_coaches)].to_dict(orient='records'),
        teams_by_league=teams_by_league,
        timeline_data=timeline_data
    )


@app.route('/select-team', methods=['POST'])
def select_team():
    # Randomly select a team for a given league
    data = request.get_json()
    league = data.get('league')
    if league and league in df_teams['league'].unique():
        teams = df_teams[df_teams['league'] == league]['team_name'].tolist()
        selected_team = random.choice(teams) if teams else None
        return jsonify({"team": selected_team}), 200
    return jsonify({"error": "Invalid league"}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Default to port 5000 if PORT is not set
    app.run(host="0.0.0.0", port=port)