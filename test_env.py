from custom_env import SimpleWalkerEnv
import numpy as np

env = SimpleWalkerEnv(render_mode=None)
obs, _ = env.reset()
print("Environment created successfully.")
print("Observation shape:", obs.shape)

action = env.action_space.sample()
obs, reward, terminated, truncated, info = env.step(action)
print("Step successful.")
print("Reward:", reward)
env.close()
