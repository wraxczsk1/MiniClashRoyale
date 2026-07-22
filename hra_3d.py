import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random
from contextlib import contextmanager


@contextmanager
def push_matrix():
    """Uloží a obnoví aktuální matici kolem vykreslení objektu."""
    glPushMatrix()
    try:
        yield
    finally:
        glPopMatrix()


def distance3d(a, b):
    """Euklidovská vzdálenost mezi dvěma objekty s atributy x, y, z."""
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)


class Entity:
    """Základ pro objekty ve scéně se společnou pozicí a velikostí."""

    def __init__(self, x, y, z, size):
        self.x = x
        self.y = y
        self.z = z
        self.size = size

    def render(self, color, rotation=None):
        with push_matrix():
            glTranslatef(self.x, self.y, self.z)
            if rotation is not None:
                glRotatef(rotation, 1, 1, 1)
            glColor3f(*color)
            self.draw_shape()

    def draw_shape(self):
        raise NotImplementedError


# Inicializace
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
pygame.display.set_caption("3D Hra - Letadlo")

# Nastavení OpenGL
gluPerspective(45, (display[0] / display[1]), 0.1, 500.0)
glTranslatef(0.0, -1.0, -5.0)
glEnable(GL_DEPTH_TEST)

class Letadlo(Entity):
    def __init__(self):
        super().__init__(0, 0, 0, 0.3)

    def draw(self):
        self.render((0.0, 1.0, 0.0))  # Zelená

    def draw_shape(self):
        glBegin(GL_TRIANGLES)
        # Přední strana
        glColor3f(0, 1, 0)
        glVertex3f(0, self.size, 0)
        glVertex3f(-self.size, -self.size, self.size)
        glVertex3f(self.size, -self.size, self.size)
        
        # Zadní strana
        glColor3f(0, 0.7, 0)
        glVertex3f(0, self.size, 0)
        glVertex3f(self.size, -self.size, -self.size)
        glVertex3f(-self.size, -self.size, -self.size)
        
        # Levá strana
        glColor3f(0, 1, 0)
        glVertex3f(0, self.size, 0)
        glVertex3f(-self.size, -self.size, -self.size)
        glVertex3f(-self.size, -self.size, self.size)
        
        # Pravá strana
        glColor3f(0, 0.7, 0)
        glVertex3f(0, self.size, 0)
        glVertex3f(self.size, -self.size, self.size)
        glVertex3f(self.size, -self.size, -self.size)
        glEnd()
    
    def move(self, dx, dy, dz):
        self.x += dx
        self.y += dy
        self.z += dz
        
        # Omezení pohybu
        if self.x > 3: self.x = 3
        if self.x < -3: self.x = -3
        if self.y > 2: self.y = 2
        if self.y < -2: self.y = -2

class Asteroid(Entity):
    def __init__(self):
        super().__init__(
            random.uniform(-3, 3),
            random.uniform(-2, 2),
            random.uniform(-15, -1),
            random.uniform(0.1, 0.4),
        )
        self.vz = random.uniform(0.05, 0.15)
        self.rotation = 0

    def draw(self):
        self.render((0.8, 0.4, 0.2), rotation=self.rotation)  # Oranžová
        self.rotation += 2

    def draw_shape(self):
        glBegin(GL_TRIANGLES)
        vertices = [
            [-self.size, -self.size, -self.size],
            [self.size, -self.size, -self.size],
            [self.size, self.size, -self.size],
            [-self.size, self.size, -self.size],
            [-self.size, -self.size, self.size],
            [self.size, -self.size, self.size],
            [self.size, self.size, self.size],
            [-self.size, self.size, self.size]
        ]
        
        faces = [
            [0, 1, 2], [0, 2, 3],
            [4, 6, 5], [4, 7, 6],
            [0, 4, 5], [0, 5, 1],
            [2, 6, 7], [2, 7, 3],
            [0, 3, 7], [0, 7, 4],
            [1, 5, 6], [1, 6, 2]
        ]
        
        for face in faces:
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()
    
    def update(self):
        self.z += self.vz

def detect_collision(letadlo, asteroid):
    return distance3d(letadlo, asteroid) < (letadlo.size + asteroid.size)

# Hlavní smyčka
letadlo = Letadlo()
asteroidy = [Asteroid() for _ in range(5)]
skore = 0
game_over = False
clock = pygame.time.Clock()

print("🚀 3D HRA - VYHNI SE ASTEROIDŮM")
print("Klávesy: ŠIPKY pro pohyb, ESC pro exit")
print("=" * 40)

running = True
while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
    
    # Ovládání
    keys = pygame.key.get_pressed()
    if keys[K_LEFT]:
        letadlo.move(-0.1, 0, 0)
    if keys[K_RIGHT]:
        letadlo.move(0.1, 0, 0)
    if keys[K_UP]:
        letadlo.move(0, 0.1, 0)
    if keys[K_DOWN]:
        letadlo.move(0, -0.1, 0)
    
    # Aktualizace asteroidů
    for asteroid in asteroidy:
        asteroid.update()
        if asteroid.z > 1:
            asteroidy.remove(asteroid)
            asteroidy.append(Asteroid())
            skore += 1
        
        # Detekce kolize
        if detect_collision(letadlo, asteroid):
            game_over = True
    
    # Vykreslování
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0.05, 0.05, 0.1, 1)
    
    letadlo.draw()
    for asteroid in asteroidy:
        asteroid.draw()
    
    pygame.display.flip()
    
    if game_over:
        print(f"\n💥 GAME OVER! Skóre: {skore}")
        break

pygame.quit()
print("Hra skončila!")
