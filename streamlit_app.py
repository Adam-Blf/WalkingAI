import streamlit as st
import pandas as pd
import os
import time
import subprocess
import sys

# Configuration de la page
st.set_page_config(
    page_title="Walking AI Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .metric-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #4b4b4b;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Walking AI - Reinforcement Learning Control Center")

# Sidebar
with st.sidebar:
    st.header("🎮 Contrôles")
    mode = st.radio("Mode", ["Visualisation", "Entraînement"])
    
    st.markdown("---")
    st.markdown("### 📊 Modèles")
    models_dir = "models/PPO"
    if os.path.exists(models_dir):
        models = sorted([f for f in os.listdir(models_dir) if f.endswith(".zip")])
        selected_model = st.selectbox("Choisir un checkpoint", models, index=len(models)-1 if models else 0)
    else:
        st.warning("Aucun modèle trouvé")
        selected_model = None

# Main Content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("État de l'Agent")
    if mode == "Visualisation":
        st.info("Le mode visualisation lancera une fenêtre native PyGame pour afficher la simulation physique.")
        
        if st.button("🚀 Lancer la Simulation", type="primary", use_container_width=True):
            if selected_model:
                with st.spinner("Démarrage de l'environnement..."):
                    # Lancer visualize.py en sous-processus
                    try:
                        subprocess.Popen([sys.executable, "visualize.py"])
                        st.success("Simulation lancée dans une nouvelle fenêtre !")
                    except Exception as e:
                        st.error(f"Erreur au lancement: {e}")
            else:
                st.error("Veuillez sélectionner un modèle.")
                
    elif mode == "Entraînement":
        st.warning("L'entraînement est un processus long qui utilisera beaucoup de ressources CPU/GPU.")
        timesteps = st.number_input("Timesteps", value=100000, step=10000)
        if st.button("🏋️ Commencer l'entraînement"):
            st.code(f"python train.py --timesteps {timesteps}")
            st.info("Pour l'instant, lancez cette commande dans votre terminal pour voir les logs en temps réel.")

with col2:
    st.subheader("Métriques")
    # Simulation de métriques pour l'UI (à connecter aux vrais logs Tensorboard plus tard)
    st.markdown("""
    <div class="metric-card">
        <h4>Dernière Récompense Moyenne</h4>
        <h2>452.3</h2>
        <p style="color: #00ff00;">+12% vs précédent</p>
    </div>
    <br>
    <div class="metric-card">
        <h4>Durée de l'épisode</h4>
        <h2>12.5s</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📈 Progression")
    chart_data = pd.DataFrame({
        'Reward': [10, 25, 40, 35, 80, 120, 200, 350, 450],
        'Steps': range(0, 90000, 10000)
    }).set_index('Steps')
    st.line_chart(chart_data)

st.markdown("---")
st.caption("Walking AI Project - Powered by Gymnasium & Stable Baselines3")
