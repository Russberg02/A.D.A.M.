import streamlit as st
import pandas as pd
from pickle import load
import pickle
import numpy as np
import math as m
import matplotlib.pyplot as plt
from PIL import Image
import os
from glob import glob

st.set_page_config(layout="wide")
st.title("Advanced corrodeD pipe structurAl integrity systeM (ADAM)")

# Sidebar Inputs
st.sidebar.header("User Input Parameters")
def user_input_features():
    t = st.sidebar.number_input('Pipe Thickness, t (mm)', value=10.0)
    D = st.sidebar.number_input('Pipe Diameter, D (mm)', value=100.0)
    L = st.sidebar.number_input('Pipe Length, L (mm)', value=1000.0)
    Lc = st.sidebar.number_input('Corrosion Length, Lc (mm)', value=100.0)
    Dc = st.sidebar.number_input('Corrosion Depth, Dc (mm)', value=5.0)
    Sy = st.sidebar.number_input('Yield Stress, Sy (MPa)', value=300.0)
    UTS = st.sidebar.number_input('Ultimate Tensile Strength, UTS (MPa)', value=450.0)
    Pop_Max = st.sidebar.slider('Max Operating Pressure, Pmax (MPa)', 0, 50, 20)
    Pop_Min = st.sidebar.slider('Min Operating Pressure, Pmin (MPa)', 0, 50, 10)
    return t, D, L, Lc, Dc, Sy, UTS, Pop_Max, Pop_Min

t, D, L, Lc, Dc, Sy, UTS, Pop_Max, Pop_Min = user_input_features()

# Calculations
Pvm = 4 * t * UTS / (m.sqrt(3) * D)
PTresca = 2 * t * UTS / D
M = m.sqrt(1 + 0.8 * (L / m.sqrt(D * t)))
if L < m.sqrt(20 * D * t):
    P_ASME_B31G = (2 * t * UTS / D) * (1 - (2/3)*(Dc/t)) / (1 - (2/3)*(Dc/t)/M)
else:
    P_ASME_B31G = (2 * t * UTS / D) * (1 - (Dc/t))

Q = m.sqrt(1 + 0.31 * (Lc**2) / (D * t))
P_DnV = (2 * UTS * t / (D - t)) * ((1 - Dc/t) / (1 - Dc/(t * Q)))
P_PCORRC = (2 * t * UTS / D) * (1 - Dc/t)

# Display results
st.subheader("Burst Pressure Results")
df_pressures = pd.DataFrame({
    "Method": ["Von Mises", "Tresca", "ASME B31G", "DnV", "PCORRC"],
    "Burst Pressure (MPa)": [Pvm, PTresca, P_ASME_B31G, P_DnV, P_PCORRC]
})
st.dataframe(df_pressures)

st.bar_chart(df_pressures.set_index("Method"))

# Von Mises Stresses
P1max = Pop_Max * D / (2 * t)
P2max = Pop_Max * D / (4 * t)
P1min = Pop_Min * D / (2 * t)
P2min = Pop_Min * D / (4 * t)

σ_vm_max = (1 / m.sqrt(2)) * m.sqrt((P1max - P2max)**2 + (P2max)**2 + (P1max)**2)
σ_vm_min = (1 / m.sqrt(2)) * m.sqrt((P1min - P2min)**2 + (P2min)**2 + (P1min)**2)

# Fatigue Criteria Values
σ_a = (σ_vm_max - σ_vm_min) / 2
σ_m = (σ_vm_max + σ_vm_min) / 2
Se = 0.5 * UTS
SF = 1

goodman = (σ_a / (Se / SF)) + (σ_m / UTS)
gerber = (σ_m / UTS)**2 + (σ_a / Se)
soderberg = (σ_a / Se) + (σ_m / Sy)
morrow = (σ_a / Se) + (σ_m / SF)

fatigue_results = pd.DataFrame({
    "Criterion": ["Goodman", "Gerber", "Soderberg", "Morrow"],
    "Value": [goodman, gerber, soderberg, morrow]
})
st.subheader("Fatigue Criteria Values")
st.dataframe(fatigue_results)

st.subheader("Fatigue Criteria Comparison")
st.bar_chart(fatigue_results.set_index("Criterion"))

# Goodman, Gerber, Soderberg, Morrow Graph
sigma_a_vals = np.linspace(0, Se * 1.2, 300)
goodman_m = UTS * (1 - sigma_a_vals / Se)
gerber_m = UTS * np.sqrt(np.clip(1 - (sigma_a_vals / Se)**2, 0, None))
soderberg_m = Sy * (1 - sigma_a_vals / Se)
morrow_m = UTS * (1 - sigma_a_vals / Se)

fig, ax = plt.subplots(figsize=(10, 6))
safe_limit = np.minimum.reduce([goodman_m, gerber_m, soderberg_m, morrow_m])
ax.fill_between(sigma_a_vals, 0, safe_limit, color='green', alpha=0.1, label='Safe Region')
ax.plot(sigma_a_vals, goodman_m, label='Goodman', color='blue', linewidth=2)
ax.plot(sigma_a_vals, gerber_m, label='Gerber', color='red', linewidth=2)
ax.plot(sigma_a_vals, soderberg_m, label='Soderberg', color='orange', linewidth=2)
ax.plot(sigma_a_vals, morrow_m, label='Morrow (approx)', color='purple', linestyle='--', linewidth=2)
ax.set_xlabel("Alternating Stress σₐ (MPa)")
ax.set_ylabel("Mean Stress σₘ (MPa)")
ax.set_title("Fatigue Failure Criteria")
ax.legend()
ax.grid(True)
st.pyplot(fig)
