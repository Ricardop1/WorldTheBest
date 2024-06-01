import pandas as pd
import plotly.express as px
import streamlit as st

# Load the data into a pandas DataFrame
df = pd.read_csv('./thebest.csv')

st.dataframe(df)
# Group by 'equipo' to count victories per team
equipo_counts = df['equipo'].value_counts().reset_index()
equipo_counts.columns = ['equipo', 'victories']

# Group by 'entrenador' to count victories per coach
entrenador_counts = df['entrenador'].value_counts().reset_index()
entrenador_counts.columns = ['entrenador', 'victories']

# Create a plotly bar plot for equipo
fig_equipo = px.bar(equipo_counts, x='equipo', y='victories', 
                    title='Victories by Team', labels={'equipo': 'Team', 'victories': 'Number of Victories'})

# Create a plotly bar plot for entrenador
fig_entrenador = px.bar(entrenador_counts, x='entrenador', y='victories', 
                        title='Victories by Coach', labels={'entrenador': 'Coach', 'victories': 'Number of Victories'})

# Use Streamlit to display the plots
st.title('Team and Coach Victory Analysis')
st.plotly_chart(fig_equipo)
st.plotly_chart(fig_entrenador)