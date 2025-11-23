import gymnasium as gym
from stable_baselines3 import PPO
import os
from custom_env import SimpleWalkerEnv

# Création des dossiers
models_dir = "models/PPO"
log_dir = "logs"

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 1. Création de l'environnement personnalisé
env = SimpleWalkerEnv(render_mode=None)

# 2. Création de l'IA
model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=log_dir)

print("-------------------------------------------------")
print("Démarrage de l'apprentissage du SimpleWalker...")
print("-------------------------------------------------")

# 3. Boucle d'apprentissage
TIMESTEPS = 10000
iters = 0
while True:
    iters += 1
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False)
    model.save(f"{models_dir}/{TIMESTEPS*iters}")
    print(f"Modèle sauvegardé : {TIMESTEPS*iters} pas.")

    if iters >= 10: # 100k pas
        break

env.close()
print("Fini ! Lancez visualize.py")
