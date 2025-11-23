import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pymunk
import pymunk.pygame_util
import pygame

class SimpleWalkerEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 50}

    def __init__(self, render_mode=None):
        super().__init__()
        self.render_mode = render_mode
        
        # Actions: Moteur Jambe Gauche, Moteur Jambe Droite (-1 à 1)
        self.action_space = spaces.Box(low=-1, high=1, shape=(2,), dtype=np.float32)
        
        # Observations: 
        # [Angle Corps, Vitesse Angulaire Corps, Pos X, Pos Y, Vitesse X, Vitesse Y, 
        #  Angle Jambe 1, Vitesse Jambe 1, Angle Jambe 2, Vitesse Jambe 2]
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(10,), dtype=np.float32)

        self.screen = None
        self.clock = None
        self.draw_options = None

        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # Initialisation Pymunk
        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)
        
        # Sol
        ground = pymunk.Segment(self.space.static_body, (-1000, 50), (10000, 50), 5.0)
        ground.friction = 1.0
        ground.filter = pymunk.ShapeFilter(group=1)
        self.space.add(ground)

        # Création du Robot
        self._create_robot()
        
        self.steps = 0
        self.prev_x = self.body.position.x
        
        return self._get_obs(), {}

    def _create_robot(self):
        # Corps
        mass = 10
        radius = 20
        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = (200, 200)
        shape = pymunk.Circle(self.body, radius)
        shape.friction = 0.5
        shape.filter = pymunk.ShapeFilter(group=2) # Ne collisionne pas avec ses propres jambes
        self.space.add(self.body, shape)

        # Jambes
        self.legs = []
        self.motors = []
        
        for i in range(2):
            leg_mass = 2
            leg_w, leg_h = 10, 60
            leg_moment = pymunk.moment_for_box(leg_mass, (leg_w, leg_h))
            leg_body = pymunk.Body(leg_mass, leg_moment)
            leg_body.position = (200, 160)
            leg_shape = pymunk.Poly.create_box(leg_body, (leg_w, leg_h))
            leg_shape.friction = 1.0
            leg_shape.filter = pymunk.ShapeFilter(group=2)
            
            # Pivot (Hanche)
            pivot = pymunk.PivotJoint(self.body, leg_body, (0, 0), (0, leg_h/2))
            pivot.collide_bodies = False
            
            # Moteur
            motor = pymunk.SimpleMotor(self.body, leg_body, 0)
            motor.max_force = 100000
            
            self.space.add(leg_body, leg_shape, pivot, motor)
            self.legs.append(leg_body)
            self.motors.append(motor)

    def _get_obs(self):
        # Récupération des données physiques
        body_angle = self.body.angle
        body_vel = self.body.velocity
        
        obs = [
            self.body.angle,
            self.body.angular_velocity,
            self.body.position.x,
            self.body.position.y,
            self.body.velocity.x,
            self.body.velocity.y,
            self.legs[0].angle - self.body.angle,
            self.legs[0].angular_velocity,
            self.legs[1].angle - self.body.angle,
            self.legs[1].angular_velocity
        ]
        return np.array(obs, dtype=np.float32)

    def step(self, action):
        self.steps += 1
        
        # Appliquer l'action (Vitesse des moteurs)
        # On limite la vitesse pour simuler des servos
        self.motors[0].rate = float(action[0]) * 5.0
        self.motors[1].rate = float(action[1]) * 5.0
        
        # Simulation physique (50 FPS)
        dt = 1.0 / 50.0
        self.space.step(dt)
        
        # Calcul de la récompense
        current_x = self.body.position.x
        forward_reward = (current_x - self.prev_x) * 10.0 # Encourager à avancer
        self.prev_x = current_x
        
        # Pénalité pour l'énergie utilisée (pour éviter de vibrer)
        energy_penalty = np.mean(np.abs(action)) * 0.1
        
        # Pénalité si le corps touche le sol (trop bas) ou trop penché
        terminated = False
        penalty = 0
        
        if self.body.position.y < 80: # Tombé
            terminated = True
            penalty = -100
        
        if abs(self.body.angle) > 1.0: # Trop penché
            terminated = True
            penalty = -100

        reward = forward_reward - energy_penalty + penalty
        
        # Bonus pour rester en vie
        reward += 0.1

        truncated = self.steps >= 1000
        
        if self.render_mode == "human":
            self.render()

        return self._get_obs(), reward, terminated, truncated, {}

    def render(self):
        if self.screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode((800, 400))
            pygame.display.set_caption("Walking AI - Training Visualization")
            self.clock = pygame.time.Clock()
            # Load fonts
            self.font = pygame.font.SysFont("Arial", 16)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()

        # Dark Background
        self.screen.fill((20, 20, 30))
        
        # Camera offset
        offset_x = -self.body.position.x + 400
        offset_y = 0 # Pymunk Y is up, Pygame Y is down. We need to handle this.
        
        # Helper to convert Pymunk pos to Pygame pos
        def to_pygame(p):
            return int(p.x + offset_x), int(400 - p.y)

        # Draw Floor (Grid)
        floor_y = 400 - 50
        pygame.draw.line(self.screen, (0, 255, 200), (-1000 + offset_x, floor_y), (10000 + offset_x, floor_y), 2)
        
        # Grid lines
        start_grid = int(self.body.position.x // 50) * 50 - 400
        for x in range(start_grid, start_grid + 900, 50):
            screen_x = x + offset_x
            pygame.draw.line(self.screen, (40, 40, 60), (screen_x, 0), (screen_x, 400), 1)

        # Draw Legs
        for i, leg in enumerate(self.legs):
            # Get vertices in world coordinates
            poly = leg.shapes.pop() # Hack to get shape
            leg.shapes.add(poly) # Put it back
            
            # Vertices are relative to body position and rotation
            # We can use pymunk's built-in transformation
            verts = []
            for v in poly.get_vertices():
                p = v.rotated(leg.angle) + leg.position
                verts.append(to_pygame(p))
            
            color = (0, 150, 255) if i == 0 else (0, 100, 200) # Different colors for legs
            pygame.draw.polygon(self.screen, color, verts)
            pygame.draw.polygon(self.screen, (200, 200, 255), verts, 2) # Border

        # Draw Body
        body_pos = to_pygame(self.body.position)
        pygame.draw.circle(self.screen, (255, 50, 50), body_pos, 20) # Red Core
        pygame.draw.circle(self.screen, (255, 255, 255), body_pos, 20, 2) # White Border
        
        # Draw Eye/Orientation
        eye_pos = self.body.position + pymunk.Vec2d(15, 0).rotated(self.body.angle)
        pygame.draw.circle(self.screen, (255, 255, 0), to_pygame(eye_pos), 5)

        # HUD
        dist_text = self.font.render(f"Distance: {self.body.position.x:.1f}m", True, (255, 255, 255))
        step_text = self.font.render(f"Steps: {self.steps}", True, (255, 255, 255))
        self.screen.blit(dist_text, (10, 10))
        self.screen.blit(step_text, (10, 30))

        pygame.display.flip()
        self.clock.tick(50)

    def close(self):
        if self.screen is not None:
            pygame.quit()
            self.screen = None
