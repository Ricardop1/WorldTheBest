import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
st.title('WORLD THE BEST')

df = pd.read_csv("./thebest.csv")

st.dataframe(df)
# Group by the 'equipo' column
grouped_equipo_df = df.groupby('equipo').sum()  # or any other aggregation function

st.dataframe(grouped_equipo_df)

# Create a plot
fig, ax = plt.subplots()
grouped_equipo_df.plot(kind='bar', ax=ax)
ax.set_title('Grouped by Equipo')
ax.set_xlabel('Equipo')
ax.set_ylabel('Values')  # change this to the appropriate label

st.pyplot(fig)


# Group by the 'equipo' column
grouped_entrenador_df = df.groupby('entrenador').sum()  # or any other aggregation function

# Create a plot
fig, ax = plt.subplots()
grouped_entrenador_df.plot(kind='bar', ax=ax)
ax.set_title('Grouped by Entrenador')
ax.set_xlabel('Entrenador')
ax.set_ylabel('Values')  # change this to the appropriate label

st.pyplot(fig)


# Create a plotly bar plot
fig = px.bar(grouped_equipo_df, x=grouped_equipo_df.index, y=grouped_equipo_df.columns,
             title='Grouped by Equipo', labels={'x': 'Equipo', 'y': 'Values'})

st.plotly_chart(fig)


# Create a plotly bar plot
fig = px.bar(grouped_entrenador_df, x=grouped_entrenador_df.index, y=grouped_entrenador_df.columns,
             title='Grouped by Entrenador', labels={'x': 'Entrenador', 'y': 'Values'})
st.plotly_chart(fig)