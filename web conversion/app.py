from flask import Flask, render_template, jsonify, request, url_for, redirect, session
import pandas as pd
import json
import random
import os
from google_api import generate
from prompts import FOOT_ANALYST
from dotenv import load_dotenv

load_dotenv()  # Add this line after your imports

app = Flask(__name__, static_url_path='/static')
app.secret_key = os.urandom(24)


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

@app.route('/new-edition', methods=['GET', 'POST'])
def new_edition():
    if request.method == 'POST':
        data = request.form
        num_teams = int(data.get('num_teams'))
        selected_teams = [data.get(f'team_{i}') for i in range(1, num_teams + 1)]
        tournament_format = data.get('tournament_format')
        matchups = data.get('matchups')
        groups = data.get('groups')

        # Prepare input for LLM
        list_of_champions = df.to_string(index=False)
        input_text = FOOT_ANALYST.format(
            list_of_champions=list_of_champions,
            list_of_teams=selected_teams,
            tournament_format=tournament_format
        )

        # Call LLM to predict results
        prediction = generate(input_text, os.getenv("GEMINI_API_KEY"))

        return render_template('prediction_result.html', prediction=prediction)

    teams = df_teams['team_name'].tolist()
    # Create a dictionary of team to coach mappings
    team_coaches = df_team_coach.set_index('team_name')['long_name'].to_dict()
    return render_template('new_edition.html', teams=teams, team_coaches=team_coaches)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    format_type = data['format']
    teams = data['teams']
    matchups = data['matchups']
    team_assignments = data['teamAssignments']

    # Create coach assignments string
    def get_coach_name(team, assignment):
        if assignment == 'low':
            return 'Joachim Low'
        elif assignment == 'patrick':
            return 'Rick Patrick'
        else:
            # Get coach from team_coach.csv
            coach = df_team_coach[df_team_coach['team_name'] == team]['long_name'].values
            return coach[0] if len(coach) > 0 else 'Unknown Coach'

    # Format teams with coach assignments
    teams_with_coaches = [
        f"{team} (Coach: {get_coach_name(team, team_assignments.get(team, None))})" 
        for team in teams if team
    ]
    # and team_assignments.get(team, None) in ['low', 'patrick'] else team
    # Format matchups string
    matchups_str = ""
    if format_type == "Eliminatoria directa":
        matchups_str = "\nMatchups:\n" + "\n".join(
            f"Round {m['round']}, Match {m['match']}: {m['team1']} vs {m['team2']}"
            for m in matchups
        )
    elif format_type == "Grupos y eliminatorias":
        matchups_str = "\nGroups:\n" + "\n".join(
            f"Group {m['group']}: " + ", ".join(m['teams'])
            for m in matchups
        )

    # Format the prompt
    list_of_champions = df.to_string(index=False)
    input_text = FOOT_ANALYST.format(
        list_of_champions=list_of_champions,
        list_of_teams=teams_with_coaches,  # Use teams with coach info
        tournament_format=format_type + matchups_str
    )

    try:
        # Generate prediction
        prediction = generate(input_text, os.getenv('GEMINI_API_KEY'))
        if prediction is None:
            prediction = "Error generating prediction. Please try again."
        
        # Store prediction in session
        session['prediction'] = prediction
        return jsonify({'redirect': url_for('prediction_result')})
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        return jsonify({'error': 'Failed to generate prediction'}), 500

@app.route('/prediction-result')
def prediction_result():
    prediction = session.get('prediction', 'No prediction available')
    return render_template('prediction_result.html', prediction=prediction)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
