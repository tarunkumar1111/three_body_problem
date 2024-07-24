import pygame
import math
import numpy as np
import typer
import logging

COLORS = [
    (255, 0, 0),   # Red
    (0, 255, 0),   # Green
    (0, 0, 255),   # Blue
    (255, 255, 0), # Yellow
    (255, 0, 255), # Magenta
    (0, 255, 255), # Cyan
    (128, 128, 128), # Gray
]

class Body:
    def __init__(
        self, x, y, mass, velocity, color, rebound_factor, screen_width, screen_height
    ):
        self.x = x
        self.y = y
        self.mass = mass
        self.radius = int(math.sqrt(mass) * 2)
        self.vx, self.vy = velocity
        self.color = color
        self.trace = []
        self.rebound_factor = rebound_factor
        self.screen_width = screen_width
        self.screen_height = screen_height

    def __eq__(self, other) -> bool:
        # Compares the colors of two objects to determine if they are equal.
        # Returns True if the colors match, otherwise False.
        if self.color == other.color:
            return True
        else:
            return False

    def calculate_grav_force(self, bodies: list, g: float):
        # Calculates the cumulative gravitational force exerted by a list of bodies on the current object.
        # Iterates through each body in the list, excluding itself, to sum the gravitational forces.
        # Updates the object's position and velocity based on the resulting force.
        force = (0, 0)
        for body in bodies:
            if body != self:
                force += calculate_gravitational_force(self, body, g)
        force1x, force1y = add_tuples(force)
        self.update(force1x, force1y)

    def update(self, force_x: float, force_y: float):
        # Updates the object's position and velocity using the applied force.
        # Calculates acceleration based on the force and updates velocities and positions accordingly.
        # Ensures the object stays within boundaries and updates its path trace.
        ax = force_x / self.mass
        ay = force_y / self.mass
        self.vx += ax
        self.vy += ay
        self.x += self.vx
        self.y += self.vy
        self.check_boundaries()
        self.update_trace()

    def update_trace(self):
        # Adds the current position (x, y) of the object to its trace.
        # Maintains a fixed length of 100 points by removing the oldest point when necessary.
        self.trace.append((self.x, self.y))
        if len(self.trace) == 100:
            self.trace.pop(0)

    def check_boundaries(self):
        # Checks and adjusts the object's position and velocity to ensure it stays within screen boundaries.
        # Reverses velocity with a rebound factor if the object hits the screen edges.
        if self.y < 0:
            self.y = 0
            self.vy *= -self.rebound_factor
        elif self.y > self.screen_height:
            self.y = self.screen_height
            self.vy *= -self.rebound_factor
        if self.x < 0:
            self.x = 0
            self.vx *= -self.rebound_factor
        elif self.x > self.screen_width:
            self.x = self.screen_width
            self.vx *= -self.rebound_factor

    def draw(self, screen):
        # Draws the object on the specified Pygame screen.
        # Uses the object's color and radius to draw the current position and its path trace.
        for point in self.trace:
            pygame.draw.circle(screen, self.color, point, 1)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

def calculate_gravitational_force(p1: Body, p2: Body, g: float) -> tuple:
    # Calculates the gravitational force between two bodies using Newton's law of universal gravitation.
    # Returns a tuple with the horizontal and vertical components of the force.
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    distance = max(1, math.sqrt(dx**2 + dy**2))
    if distance < 40:
        return (0, 0)
    force = (g * p1.mass * p2.mass) / (distance**2)
    angle = math.atan2(dy, dx)
    force_x = force * math.cos(angle)
    force_y = force * math.sin(angle)
    return (force_x, force_y)

def add_tuples(tuple: tuple) -> tuple:
    # Sums even-indexed and odd-indexed elements of the input tuple separately.
    # Returns a new tuple with the sums of even and odd elements.
    even = 0
    odd = 0
    for i in range(len(tuple)):
        if i % 2 == 0:
            even += tuple[i]
        else:
            odd += tuple[i]
    return (even, odd)

def main(
    width: int = typer.Option(800, help="Width of the screen"),
    height: int = typer.Option(600, help="Height of the screen"),
    max_bodies: int = typer.Option(
        10, help="Maximum number of bodies to had to the simulation."
    ),
    rebound_factor: float = typer.Option(
        0.5,
        help="Factor strength to apply when bodies when bodies bounce off the limits of the screen.",
    ),
    mass: int = typer.Option(10, help="Default mass of the bodies."),
    g: int = typer.Option(9.8, help="The gravitational constant."),
    clock: int = typer.Option(
        60, help="Framerate to delay the game to the given ticks."
    ),
):
    """
    Welcome to the n-body simulation, press

    """

    # SETUP
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    # CALCULATE NECESSARY TRIGONOMETRY
    side = 200
    x = np.sqrt(side**2 - (side / 2) ** 2)
    initial_x = width / 2 - side / 2
    initial_y = 400

    # INITIAL BODIES
    body1 = Body(
        initial_x,
        initial_y,
        mass=mass,
        velocity=(0.1, 0.1),
        color=(116, 148, 196),
        rebound_factor=rebound_factor,
        screen_height=height,
        screen_width=width,
    )
    body2 = Body(
        (initial_x + (initial_x + side)) / 2,
        initial_y - x,
        mass=mass,
        velocity=(-0.1, 0.1),
        color=(106, 77, 97),
        rebound_factor=rebound_factor,
        screen_height=height,
        screen_width=width,
    )
    body3 = Body(
        initial_x + side,
        initial_y,
        mass=mass,
        velocity=(0.1, -0.1),
        color=(195, 212, 7),
        rebound_factor=rebound_factor,
        screen_height=height,
        screen_width=width,
    )
    bodies = [body1, body2, body3]

    # MAIN LOOP
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if len(bodies) < max_bodies:
                    mouse = pygame.mouse.get_pos()
                    bodies.append(
                        Body(
                            mouse[0],
                            mouse[1],
                            mass=mass,
                            velocity=(0.1, 0.1),
                            color=COLORS[len(bodies) - 3],
                            rebound_factor=rebound_factor,
                            screen_height=height,
                            screen_width=width,
                        )
                    )
                else:
                    logging.warning("You've reached the maximum of bodies!")

        screen.fill((0, 0, 0))

        for body in bodies:
            body.calculate_grav_force(bodies, g=g)
            body.draw(screen)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()
    print("Thank you for playing the simulator,we look forward to your return! ")

if __name__ == "__main__":
    typer.run(main)
