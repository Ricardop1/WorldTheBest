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

st.dataframe(df, hide_index = True)
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
    st.dataframe(equipo_counts, hide_index = True,use_container_width=True)
    st.plotly_chart(fig_equipo)
with col2:
    st.dataframe(entrenador_counts, hide_index = True,use_container_width=True)
    st.plotly_chart(fig_entrenador)


selection = dataframe_with_selections(df_teams.head(10))
st.write("Your selection:")
st.write(selection)