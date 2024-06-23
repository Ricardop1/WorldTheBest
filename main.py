import pandas as pd
import plotly.express as px
import streamlit as st


def dataframe_with_selections(df):
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Select", False)

    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config={"Select": st.column_config.CheckboxColumn(required=True)},
        disabled=df.columns,
    )

    # Filter the dataframe using the temporary column, then drop the column
    selected_rows = edited_df[edited_df.Select]
    return selected_rows.drop('Select', axis=1)


# Load the data into a pandas DataFrame
df = pd.read_csv('./thebest.csv')
df_teams = pd.read_csv('./teams.csv')

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
col1, col2= st.columns(2)

with col1:
    st.dataframe(equipo_counts, hide_index = True,use_container_width=True, column_config={
        "victories": st.column_config.NumberColumn(
            "Victories",
            format="%d 🏆",
        )
    })
    
with col2:
    st.dataframe(entrenador_counts, hide_index = True,use_container_width=True,column_config={
        "victories": st.column_config.NumberColumn(
            "Victories",
            format="%d 🏆",
        )
    })
    

col3, col4= st.columns(2)
with col3:
    st.plotly_chart(fig_equipo)

with col4:
    st.plotly_chart(fig_entrenador)

# Grouping by 'edition' and 'entrenador' to calculate cumulative victories
df['cumulative_victories'] = df.groupby('entrenador').cumcount() + 1

# Group by 'edition' and 'entrenador' and sum the victories
cumulative_victories = df.groupby(['edicion', 'entrenador']).size().groupby(level=1).cumsum().reset_index(name='victories')

# Creating the time series plot
fig_time_series = px.line(
    cumulative_victories,
    x='edicion',
    y='victories',
    color='entrenador',
    title='Cumulative Victories by Coach for Each Edition',
    markers=True
)

# Display time series plot
st.plotly_chart(fig_time_series)




# Grouping by 'edition' and 'entrenador' to count victories
# df['cumulative_victories_2'] = df.groupby('entrenador').cumcount() + 1

# Creating the cumulative time series plot
# fig_time_series =px.line(df, x="edicion", y="cumulative_victories", color="entrenador",
#              title="Evolution of Coach Victories per Edition",
#              labels={"edicion": "Edition", "cumulative_victories": "Cumulative Victories"})



# Display cumulative time series plot
# st.plotly_chart(fig_time_series)



selection = dataframe_with_selections(df_teams.head(10))
st.write("Your selection:")
st.write(selection)

if not selection.empty and st.button("SORTEAR"):
    st.write("El ganador es:")
    st.write(selection.sample().astype("object"))