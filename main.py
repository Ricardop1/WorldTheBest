import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
st.title('WORLD THE BEST')

df = pd.read_csv("./thebest.csv")


# Group by the 'equipo' column
grouped_equipo_df = df.groupby('equipo').sum()  # or any other aggregation function

# Create a plot
fig, ax = plt.subplots()
grouped_df.plot(kind='bar', ax=ax)
ax.set_title('Grouped by Equipo')
ax.set_xlabel('Equipo')
ax.set_ylabel('Values')  # change this to the appropriate label

st.pyplot(fig)


# Group by the 'equipo' column
grouped_equipo_df = df.groupby('entrenador').sum()  # or any other aggregation function

# Create a plot
fig, ax = plt.subplots()
grouped_df.plot(kind='bar', ax=ax)
ax.set_title('Grouped by Entrenador')
ax.set_xlabel('Entrenador')
ax.set_ylabel('Values')  # change this to the appropriate label

st.pyplot(fig)