import sys
import math
import random

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

display = (800, 600)


def init_game():
    """Inicializuje pygame a OpenGL. Vyvolá RuntimeError, pokud se něco nepodaří."""
    # pygame.init() vrací dvojici (úspěchy, selhání). Selhání se dříve tiše
    # ignorovala. Nekritické moduly (např. zvuk) hru nezastaví, ale problém
    # nahlásíme, místo abychom ho tiše spolkli.
    successes, failures = pygame.init()
    if failures:
        print(
            f"Varování: {failures} z {successes + failures} modulů pygame se "
            "nepodařilo inicializovat; pokračuji bez nich.",
            file=sys.stderr,
        )

    # Zobrazovací subsystém je pro hru nezbytný – jeho selhání je fatální.
    try:
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    except pygame.error as exc:
        raise RuntimeError(f"Nepodařilo se vytvořit OpenGL okno: {exc}") from exc

    pygame.display.set_caption("3D Hra - Letadlo")

    # Nastavení OpenGL
    gluPerspective(45, (display[0] / display[1]), 0.1, 500.0)
    glTranslatef(0.0, -1.0, -5.0)
    glEnable(GL_DEPTH_TEST)


class Letadlo:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.size = 0.3
    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glColor3f(0.0, 1.0, 0.0)  # Zelená
        self.draw_pyramid()
        glPopMatrix()
    
    def draw_pyramid(self):
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

class Asteroid:
    def __init__(self):
        self.x = random.uniform(-3, 3)
        self.y = random.uniform(-2, 2)
        self.z = random.uniform(-15, -1)
        self.size = random.uniform(0.1, 0.4)
        self.vz = random.uniform(0.05, 0.15)
        self.rotation = 0
    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotation, 1, 1, 1)
        glColor3f(0.8, 0.4, 0.2)  # Oranžová
        self.draw_cube()
        glPopMatrix()
        self.rotation += 2
    
    def draw_cube(self):
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
    dx = letadlo.x - asteroid.x
    dy = letadlo.y - asteroid.y
    dz = letadlo.z - asteroid.z
    distance = math.sqrt(dx**2 + dy**2 + dz**2)
    return distance < (letadlo.size + asteroid.size)


def run_game():
    """Hlavní herní smyčka. Vrací dosažené skóre."""
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

        # Aktualizace asteroidů (iterujeme přes kopii, abychom mohli
        # bezpečně měnit seznam během průchodu)
        for asteroid in list(asteroidy):
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

    return skore


def main():
    try:
        init_game()
        run_game()
    finally:
        # Uklidíme vždy, i když nastala výjimka během inicializace nebo hry,
        # aby okno/subsystémy pygame nezůstaly viset.
        pygame.quit()
    print("Hra skončila!")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print(f"Chyba: {exc}", file=sys.stderr)
        sys.exit(1)
