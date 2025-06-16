"""
Script para testar a renderização de asteroides
"""
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import random
import time

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Teste de Asteroide")
    
    # Configuração OpenGL básica
    glClearColor(0.0, 0.0, 0.2, 1.0)
    glEnable(GL_DEPTH_TEST)
    
    # Configurar projeção
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    
    # Posição inicial da câmera
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0, 0, -10)
    
    # Criar 5 asteroides em posições fixas
    asteroids = []
    for i in range(5):
        angle = i * (2 * math.pi / 5)
        asteroid = {
            'position': np.array([5 * math.cos(angle), 0, 5 * math.sin(angle)]),
            'rotation': np.array([random.uniform(0, 360) for _ in range(3)]),
            'scale': 0.5 + i * 0.2  # Tamanhos diferentes
        }
        asteroids.append(asteroid)
    
    # Loop principal
    clock = pygame.time.Clock()
    running = True
    rotation = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Limpar buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Rotação da cena
        glLoadIdentity()
        glTranslatef(0, 0, -10)
        glRotatef(rotation, 0, 1, 0)
        
        # Desenhar asteroides
        for i, asteroid in enumerate(asteroids):
            glPushMatrix()
            
            # Posição
            glTranslatef(asteroid['position'][0], 
                         asteroid['position'][1], 
                         asteroid['position'][2])
            
            # Rotação
            for axis, angle in enumerate(asteroid['rotation']):
                if axis == 0:  # X
                    glRotatef(angle, 1, 0, 0)
                elif axis == 1:  # Y
                    glRotatef(angle, 0, 1, 0)
                else:  # Z
                    glRotatef(angle, 0, 0, 1)
            
            # Escala
            glScalef(asteroid['scale'], asteroid['scale'], asteroid['scale'])
            
            # Cor diferente para cada asteroide
            colors = [
                (1.0, 0.0, 0.0),  # Vermelho
                (1.0, 1.0, 0.0),  # Amarelo
                (0.0, 1.0, 0.0),  # Verde
                (0.0, 1.0, 1.0),  # Ciano
                (1.0, 0.0, 1.0)   # Magenta
            ]
            glColor3f(*colors[i])
            
            # Desenhar asteroide como uma esfera
            quadric = gluNewQuadric()
            gluSphere(quadric, 1.0, 16, 16)
            gluDeleteQuadric(quadric)
            
            # Desenhar eixos para referência
            glBegin(GL_LINES)
            # Eixo X - Vermelho
            glColor3f(1, 0, 0)
            glVertex3f(0, 0, 0)
            glVertex3f(1.5, 0, 0)
            # Eixo Y - Verde
            glColor3f(0, 1, 0)
            glVertex3f(0, 0, 0)
            glVertex3f(0, 1.5, 0)
            # Eixo Z - Azul
            glColor3f(0, 0, 1)
            glVertex3f(0, 0, 0)
            glVertex3f(0, 0, 1.5)
            glEnd()
            
            glPopMatrix()
        
        # Atualizar rotação
        rotation += 0.5
        
        # Trocar buffers
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
