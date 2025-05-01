import streamlit as st
import pandas as pd
from pickle import load
import pickle
import numpy as np
import math as m
from PIL import Image
import os
from glob import glob
import matplotlib.pyplot as plt

# Page setup
st.set_page_config(page_title="ADAM - Fatigue Criteria Module", layout="centered")
st.title("ADAM: Advanced corrodeD pipe structurAl integrity systeM")
st.subheader("Fatigue Criteria Analysis (Goodman, Gerber, Soderberg, Morrow)")

# Input section
st.sidebar.header("Input Parameters")

Sut = st.sidebar.number_input("Ultimate tensile strength, Sut (MPa)", min_value=0.0, value=550.0)
Sy = st.sidebar.number_input("Yield strength, Sy (MPa)", min_value=0.0, value=350.0)
Se = st.sidebar.number_input("Endurance limit, Se (MPa)", min_value=0.0, value=275.0)
Sf = st.sidebar.number_input("Fatigue strength coefficient, Sf (MPa)", min_value=0.0, value=1000.0)
b = st.sidebar.number_input("Fatigue strength exponent, b", min_value=-1.0, max_value=0.0, value=-0.12)

# Stress input
sigma_m = st.sidebar.slider("Mean Stress (MPa)", min_value=0.0, max_value=Sut, value=100.0)
sigma_a = st.sidebar.slider("Alternating Stress (MPa)", min_value=0.0, max_value=Se, value=50.0)

# Life input
N = st.sidebar.number_input("Number of cycles (N)", min_value=1.0, value=1e5)

# Calculations
def goodman(sigma_a, sigma_m, Se, Sut):
    return sigma_a / Se + sigma_m / Sut

def gerber(sigma_a, sigma_m, Se, Sut):
    return sigma_a / Se + (sigma_m / Sut)**2

def soderberg(sigma_a, sigma_m, Se, Sy):
    return sigma_a / Se + sigma_m / Sy

def morrow(sigma_a, sigma_m, Sf, b, N):
    return sigma_a / (Sf * (2 * N) ** b) + sigma_m / Sut

goodman_val = goodman(sigma_a, sigma_m, Se, Sut)
gerber_val = gerber(sigma_a, sigma_m, Se, Sut)
soderberg_val = soderberg(sigma_a, sigma_m, Se, Sy)
morrow_val = morrow(sigma_a, sigma_m, Sf, b, N)

# Output section
st.write("### Fatigue Criteria Results")
col1, col2 = st.columns(2)

col1.metric("Goodman Index", f"{goodman_val:.3f}", delta="Safe" if goodman_val <= 1 else "Unsafe")
col1.metric("Gerber Index", f"{gerber_val:.3f}", delta="Safe" if gerber_val <= 1 else "Unsafe")
col2.metric("Soderberg Index", f"{soderberg_val:.3f}", delta="Safe" if soderberg_val <= 1 else "Unsafe")
col2.metric("Morrow Index", f"{morrow_val:.3f}", delta="Safe" if morrow_val <= 1 else "Unsafe")

# Plotting
fig, ax = plt.subplots(figsize=(6, 6))
sigma_m_vals = np.linspace(0, Sut, 500)

goodman_line = Se * (1 - sigma_m_vals / Sut)
gerber_line = Se * (1 - (sigma_m_vals / Sut)**2)
soderberg_line = Se * (1 - sigma_m_vals / Sy)

ax.plot(sigma_m_vals, goodman_line, label="Goodman", color="blue")
ax.plot(sigma_m_vals, gerber_line, label="Gerber", color="green")
ax.plot(sigma_m_vals, soderberg_line, label="Soderberg", color="red")
ax.axhline(y=Se, linestyle="--", color="gray", alpha=0.7)
ax.scatter(sigma_m, sigma_a, color="black", label="Operating Point")

ax.set_title("Fatigue Criteria Curves")
ax.set_xlabel("Mean Stress (MPa)")
ax.set_ylabel("Alternating Stress (MPa)")
ax.grid(True)
ax.legend()
st.pyplot(fig)
