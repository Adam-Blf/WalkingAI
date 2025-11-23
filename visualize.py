import gymnasium as gym
from stable_baselines3 import PPO
import os
from custom_env import SimpleWalkerEnv

# Chemin vers le modèle
models_dir = "models/PPO"
model_path = f"{models_dir}/100000.zip"

# Création de l'environnement avec rendu
env = SimpleWalkerEnv(render_mode="human")

if not os.path.exists(model_path):
    print(f"Erreur : {model_path} introuvable. Lancez train.py.")
    exit()

model = PPO.load(model_path, env=env)

print("Démonstration...")
obs, _ = env.reset()

try:
    while True:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            obs, _ = env.reset()
except KeyboardInterrupt:
    print("Arrêt.")
finally:
    env.close()
