import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT, KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, K_ESCAPE, K_c, K_p, K_o, K_PLUS, K_KP_PLUS, K_MINUS, K_KP_MINUS, K_w, K_s, K_a, K_d, K_SPACE, K_LSHIFT
from OpenGL.GL import (
    glClearColor, glEnable, glShadeModel, glMatrixMode, glLoadIdentity, glClear,
    glLightfv, glColorMaterial, glBindTexture, glGenTextures, glTexParameteri, glTexImage2D,
    glPushMatrix, glPopMatrix, glFrontFace, glDisable, glEnable, glBegin, glEnd, glColor3f, glVertex3f,
    glTranslatef, glRotatef, glMultMatrixf, glActiveTexture, glUniform1i, glUniform3f, glUniform1f,
    glUniformMatrix4fv, glGetUniformLocation, glUseProgram, glDrawElements, glBindVertexArray,
    glGenVertexArrays, glGenBuffers, glBindBuffer, glBufferData, glVertexAttribPointer, glEnableVertexAttribArray,
    glColor4f, glDeleteTextures, glDeleteBuffers, glDeleteVertexArrays, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
    GL_PROJECTION, GL_MODELVIEW, GL_LIGHTING, GL_LIGHT0, GL_COLOR_MATERIAL, GL_FRONT_AND_BACK,
    GL_AMBIENT_AND_DIFFUSE, GL_POSITION, GL_DIFFUSE, GL_SPECULAR, GL_SMOOTH, GL_TEXTURE_2D,
    GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_LINEAR, GL_RGBA, GL_UNSIGNED_BYTE, GL_RGB,
    GL_LINE_LOOP, GL_LINE_STRIP, GL_FLOAT, GL_FALSE, GL_ARRAY_BUFFER, GL_STATIC_DRAW, GL_ELEMENT_ARRAY_BUFFER,
    GL_TRIANGLES, GL_UNSIGNED_INT, GL_CW, GL_CCW, GL_TRUE, GL_TEXTURE0, GL_DEPTH_TEST, glLoadMatrixf,
    glGetAttribLocation
)
from OpenGL.GLU import (
    gluNewQuadric, gluQuadricTexture, gluSphere, gluDeleteQuadric, gluDisk
)
import numpy as np
import math
import time
import random
import os
import ctypes


# Importar os módulos que criamos
from collisions import *
from shading_models import get_gouraud_program, get_phong_program
import OpenGL.GL as gl

class SolarExplorer:
    def __init__(self, width=1280, height=720):
        # Inicialização do Pygame e OpenGL
        pygame.init()
        self.width, self.height = width, height
        self.screen = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Explorador do Sistema Solar")
        
        # Configurar OpenGL
        glClearColor(0.0, 0.0, 0.05, 1.0)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        
        # Configurar projeção
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # Corrigir: passar matriz transposta
        glLoadMatrixf(self.create_projection_matrix().T.astype(np.float32))
        
        # Criar texturas
        self.textures = {}
        self.load_textures()
        
        # Configurar luz
        self.setup_lighting()
        
        # Estado da câmera
        self.camera_distance = 30.0
        self.camera_rotation_h = 0  # Rotação horizontal em graus
        self.camera_rotation_v = 15  # Rotação vertical em graus
        self.camera_type = "orbit"  # "orbit" ou "free"
        self.camera_position = [0, 0, 30]  # Para câmera livres
        
        # Adicionar propriedades para câmera livre
        self.camera_yaw = -90.0  # -90 graus para começar olhando na direção Z negativa
        self.camera_pitch = 0.0
        self.camera_front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        
        # Estado da simulação
        self.simulation_speed = 1.0
        self.paused = False
        self.show_orbits = True
        
        # Estado do mouse e teclado
        self.last_mouse_pos = None
        self.keys = set()
        
        # Controle de tempo
        self.last_time = time.time()
        self.elapsed_time = 0
        self.delta_time = 0
        
        # Pontos de controle para a curva de Bézier de Marte
        self.mars_bezier_points = [
            np.array([16, 0, 0], dtype=np.float32),
            np.array([10, 5, 10], dtype=np.float32),
            np.array([-10, -5, 10], dtype=np.float32),
            np.array([-16, 0, 0], dtype=np.float32)
        ]
        
        # Asteroide
        self.asteroid = None  # {'t': float, 'target': str, 'alive': True, ...}
        self.asteroid_speed = 0.15  # velocidade de t por segundo
        self.asteroid_radius = 0.27  # igual à lua
        self.asteroid_curve = None  # pontos de controle da curva de Bézier
        self.asteroid_target_planet = None
        self.asteroid_target_planet_radius = None
        self.asteroid_target_planet_func = None
        # Limites da cena (paredes invisíveis)
        self.scene_bounds = {
            'x': (-40, 40),
            'y': (-10, 10),
            'z': (-40, 40)
        }
        # Controle de arrasto do asteroide
        self.asteroid_dragging = False
        self.asteroid_last_mouse = None

        self.gouraud_prog = get_gouraud_program()
        self.phong_prog = get_phong_program()
        self.sphere_vao, self.sphere_vbo, self.sphere_nbo, self.sphere_tbo, self.sphere_ebo, self.sphere_index_count = self.create_sphere_mesh(1.0, 32, 16)
    
    def load_textures(self):
        # Texturas para os planetas
        texture_files = {
            'sun': 'textures/sun.jpg',
            'mercury': 'textures/mercury.jpg',
            'venus': 'textures/venus.jpg',
            'earth': 'textures/earth.jpg',
            'moon': 'textures/moon.jpg',
            'mars': 'textures/mars.jpg',
            'jupiter': 'textures/jupiter.jpg',
            'saturn': 'textures/saturn.jpg',
            'stars': 'textures/stars.jpg',
            'asteroid': 'textures/asteroid.jpg'
        }
        
        # Criar diretório de texturas se não existir
        if not os.path.exists("textures"):
            os.makedirs("textures")
        
        # Carregar texturas ou criar fallbacks
        for name, file_path in texture_files.items():
            texture_id = self.load_texture(name, file_path)
            self.textures[name] = texture_id
            
    def load_texture(self, name, file_path):
        # Tentar carregar a textura do arquivo
        try:
            if os.path.exists(file_path):
                surface = pygame.image.load(file_path)
                texture_data = pygame.image.tostring(surface, 'RGBA', True)
                width, height = surface.get_size()
                
                texture_id = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, texture_id)
                
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
                
                print(f"Carregada textura: {name} de {file_path}")
                return texture_id
        except Exception as e:
            print(f"Erro ao carregar textura {name}: {e}")
        
        # Criar textura fallback
        print(f"Criando textura fallback para: {name}")
        return self.create_fallback_texture(name)
    
    def create_fallback_texture(self, name):
        # Cores para os diferentes objetos
        colors = {
            'sun': ([255, 230, 125], [255, 180, 0]),
            'mercury': ([150, 150, 150], [100, 100, 100]),
            'venus': ([255, 198, 112], [180, 112, 60]),
            'earth': ([30, 100, 200], [10, 150, 10]),
            'moon': ([200, 200, 200], [100, 100, 100]),
            'mars': ([220, 100, 50], [150, 50, 30]),
            'jupiter': ([255, 220, 180], [200, 150, 100]),
            'saturn': ([240, 220, 150], [200, 180, 120]),
            'stars': ([20, 20, 40], [5, 5, 20])
        }
        
        color1, color2 = colors.get(name, ([150, 150, 150], [100, 100, 100]))
        
        # Criar textura
        width, height = 256, 256
        texture_data = np.zeros((height, width, 3), dtype=np.uint8)
        
        for i in range(height):
            for j in range(width):
                if (i // 32 + j // 32) % 2 == 0:
                    texture_data[i, j] = color1
                else:
                    texture_data[i, j] = color2
        
        # Criar textura OpenGL
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        
        # Configurar parâmetros
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        # Carregar dados
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
        
        return texture_id
    
    def setup_lighting(self):
        # Configurar luz global
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Posição da luz (vai ser atualizada para a posição do sol)
        glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, 0, 1])
        
        # Características da luz
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 0.9, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        
        # Modelo de sombreamento suave
        glShadeModel(GL_SMOOTH)
    
    def draw_skybox(self):
        """Desenha o fundo estrelado"""
        glDisable(GL_LIGHTING)
        glPushMatrix()
        # Centraliza a skybox na posição da câmera para que ela nunca "afaste"
        if self.camera_type == "orbit":
            cam = self.get_orbit_camera_position()
        else:
            cam = np.array(self.camera_position)
        glTranslatef(cam[0], cam[1], cam[2])
        glBindTexture(GL_TEXTURE_2D, self.textures['stars'])
        glEnable(GL_TEXTURE_2D)
        glFrontFace(GL_CW)
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, 90.0, 32, 32)
        gluDeleteQuadric(quadric)
        glFrontFace(GL_CCW)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
        glEnable(GL_LIGHTING)
    
    def draw_sun(self):
        """Desenha o sol"""
        glDisable(GL_LIGHTING)  # O sol emite luz, não é iluminado
        
        glPushMatrix()
        
        # Textura do sol
        glBindTexture(GL_TEXTURE_2D, self.textures['sun'])
        glEnable(GL_TEXTURE_2D)
        
        # Rotação do sol
        sun_rotation = 15 * self.elapsed_time  # 15 graus por segundo
        glRotatef(sun_rotation, 0, 1, 0)
        
        # Desenhar esfera
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, 5.0, 32, 32)
        gluDeleteQuadric(quadric)
        
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
        
        glEnable(GL_LIGHTING)
    
    def draw_planet(self, name, radius, distance, orbit_angle, rotation_angle, texture_name=None):
        """Desenha um planeta"""
        if texture_name is None:
            texture_name = name
        
        # Calcular posição do planeta na órbita
        x = distance * math.cos(math.radians(orbit_angle))
        z = distance * math.sin(math.radians(orbit_angle))
        
        glPushMatrix()
        
        # Translação para posição orbital
        glTranslatef(x, 0, z)
        
        # Rotação própria
        glRotatef(rotation_angle, 0, 1, 0)
        
        # Textura do planeta
        glBindTexture(GL_TEXTURE_2D, self.textures[texture_name])
        glEnable(GL_TEXTURE_2D)
        
        # Desenhar o planeta
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, radius, 32, 32)
        gluDeleteQuadric(quadric)
        
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
        
        # Desenhar órbita se necessário
        if self.show_orbits:
            self.draw_orbit(distance)
        
        return x, 0, z  # Retornar posição para uso posterior (ex: para luas)
    
    def draw_orbit(self, distance):
        """Desenha a órbita como um círculo"""
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        
        # Desenhar círculo da órbita
        glColor3f(0.5, 0.5, 0.5)  # Cinza
        glBegin(GL_LINE_LOOP)
        for i in range(100):
            angle = 2.0 * math.pi * i / 100
            glVertex3f(distance * math.cos(angle), 0, distance * math.sin(angle))
        glEnd()
        
        glEnable(GL_LIGHTING)
    

    def get_orbit_camera_position(self):
        """Retorna a posição atual da câmera orbital"""
        # Converter ângulos para radianos
        h_rad = math.radians(self.camera_rotation_h)
        v_rad = math.radians(self.camera_rotation_v)
        
        # Calcular posição em coordenadas esféricas
        x = self.camera_distance * math.cos(v_rad) * math.sin(h_rad)
        y = self.camera_distance * math.sin(v_rad)
        z = self.camera_distance * math.cos(v_rad) * math.cos(h_rad)
        
        return np.array([x, y, z])
    
    # Funções auxiliares para criar matrizes manualmente (requisito do trabalho)
    def create_view_matrix(self):
        """Cria uma matriz de visualização baseada na câmera atual"""
        if self.camera_type == "orbit":
            # Câmera orbital - usar coordenadas esféricas
            camera_pos = self.get_orbit_camera_position()
            camera_target = np.array([0, 0, 0])  # Olhando para a origem
            up = np.array([0, 1, 0])
            
            # Calcular base da câmera (sistema de coordenadas)
            forward = camera_target - camera_pos
            forward = forward / np.linalg.norm(forward)
            
            right = np.cross(forward, up)
            right = right / np.linalg.norm(right)
            
            new_up = np.cross(right, forward)
            
            # Construir matriz de visualização
            view_matrix = np.identity(4, dtype=np.float32)
            view_matrix[0, 0:3] = right
            view_matrix[1, 0:3] = new_up
            view_matrix[2, 0:3] = -forward
            
            # Translação
            view_matrix[0, 3] = -np.dot(right, camera_pos)
            view_matrix[1, 3] = -np.dot(new_up, camera_pos)
            view_matrix[2, 3] = np.dot(forward, camera_pos)
            
            return view_matrix
        else:
            # Para câmera livre, usaríamos a posição e direção da câmera livre
            # Por simplicidade, vamos usar uma posição fixa olhando para a origem
            eye = np.array([0, 0, 30])
            target = np.array([0, 0, 0])
            up = np.array([0, 1, 0])
            
            # Cálculos similares ao caso da câmera orbital
            forward = target - eye
            forward = forward / np.linalg.norm(forward)
            
            right = np.cross(forward, up)
            right = right / np.linalg.norm(right)
            
            new_up = np.cross(right, forward)
            
            view_matrix = np.identity(4, dtype=np.float32)
            view_matrix[0, 0:3] = right
            view_matrix[1, 0:3] = new_up
            view_matrix[2, 0:3] = -forward
            
            view_matrix[0, 3] = -np.dot(right, eye)
            view_matrix[1, 3] = -np.dot(new_up, eye)
            view_matrix[2, 3] = np.dot(forward, eye)
            
            return view_matrix
    
    def create_projection_matrix(self):
        """Cria uma matriz de projeção perspectiva"""
        aspect = self.width / self.height
        fov_rad = math.radians(45)
        near = 0.1
        far = 100.0
        
        # Calcular componentes da matriz
        f = 1.0 / math.tan(fov_rad / 2.0)
        
        projection = np.zeros((4, 4), dtype=np.float32)
        projection[0, 0] = f / aspect
        projection[1, 1] = f
        projection[2, 2] = (far + near) / (near - far)
        projection[2, 3] = 2.0 * far * near / (near - far)
        projection[3, 2] = -1.0
        projection[3, 3] = 0.0
        
        return projection

    def update(self):
        """Atualiza o estado da simulação"""
        # Calcular tempo decorrido
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time
        
        # Só atualizar o tempo se não estiver pausado
        if not self.paused:
            # Ajustar pela velocidade da simulação
            self.elapsed_time += delta_time * self.simulation_speed
    
    def handle_events(self):
        """Processa eventos do usuário"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                self.keys.add(event.key)
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_c:
                    self.camera_type = "free" if self.camera_type == "orbit" else "orbit"
                    print(f"Câmera alterada para: {self.camera_type}")
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                    print("Simulação " + ("pausada" if self.paused else "continuada"))
                elif event.key == pygame.K_o:
                    self.show_orbits = not self.show_orbits
                elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS):
                    self.simulation_speed *= 1.5
                    print(f"Velocidade: {self.simulation_speed:.1f}x")
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.simulation_speed /= 1.5
                    print(f"Velocidade: {self.simulation_speed:.1f}x")
                # Criar asteroide com tecla 'n'
                if event.key == pygame.K_n:
                    if self.asteroid is None or not self.asteroid.get('alive', False):
                        self.spawn_asteroid()
            elif event.type == pygame.KEYUP:
                if event.key in self.keys:
                    self.keys.remove(event.key)
            # Remover controles de mouse para asteroide
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.last_mouse_pos = event.pos
                # Remover botão direito para asteroide
                elif event.button == 4:
                    self.camera_distance = max(5.0, self.camera_distance - 1.0)
                elif event.button == 5:
                    self.camera_distance = min(60.0, self.camera_distance + 1.0)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.last_mouse_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if self.last_mouse_pos:
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]
                    self.last_mouse_pos = event.pos
                    sensitivity = 0.3
                    if self.camera_type == "orbit":
                        self.camera_rotation_h += dx * sensitivity
                        self.camera_rotation_v = max(-85, min(85, self.camera_rotation_v - dy * sensitivity))
                    else:
                        pass
        self.process_keyboard()
        return True

    def process_keyboard(self):
        """Processa entradas contínuas do teclado"""
        # Movimento da câmera livre
        if self.camera_type == "free":
            speed = 0.2
            if pygame.K_w in self.keys:
                self.camera_position[2] -= speed
            if pygame.K_s in self.keys:
                self.camera_position[2] += speed
            if pygame.K_a in self.keys:
                self.camera_position[0] -= speed
            if pygame.K_d in self.keys:
                self.camera_position[0] += speed
            if pygame.K_SPACE in self.keys:
                self.camera_position[1] += speed
            if pygame.K_LSHIFT in self.keys:
                self.camera_position[1] -= speed
        # Remover movimento do asteroide com teclado

    def spawn_asteroid(self):
        """Cria um asteroide com trajetória automática para um planeta aleatório"""
        # Lista de planetas possíveis (nome, função para posição, raio)
        planet_defs = [
            ('mercury', lambda t: [
                8 * math.cos(math.radians(48 * t)),
                0,
                8 * math.sin(math.radians(48 * t))
            ], 0.38),
            ('venus', lambda t: [
                10 * math.cos(math.radians(35 * t)),
                0,
                10 * math.sin(math.radians(35 * t))
            ], 0.95),
            ('earth', lambda t: [
                14 * math.cos(math.radians(29 * t)),
                0,
                14 * math.sin(math.radians(29 * t))
            ], 1.0),
            # Marte agora tem órbita circular
            ('mars', lambda t: [
                18 * math.cos(math.radians(24 * t)),
                0,
                18 * math.sin(math.radians(24 * t))
            ], 0.53),
            ('jupiter', lambda t: [
                25 * math.cos(math.radians(13 * t)),
                0,
                25 * math.sin(math.radians(13 * t))
            ], 3.0),
            ('saturn', lambda t: [
                32 * math.cos(math.radians(9 * t)),
                0,
                32 * math.sin(math.radians(9 * t))
            ], 2.5)
        ]
        # Escolher planeta aleatório
        pname, pfunc, pradius = random.choice(planet_defs)
        # Posição do planeta no tempo atual
        tnow = self.elapsed_time
        if pname == 'mars':
            ppos = pfunc(tnow)
            if isinstance(ppos, np.ndarray):
                ppos = ppos.tolist()
        else:
            ppos = pfunc(tnow)
        # Ponto inicial aleatório dentro dos limites da cena (exceto perto do planeta)
        while True:
            x = random.uniform(self.scene_bounds['x'][0]+5, self.scene_bounds['x'][1]-5)
            y = random.uniform(self.scene_bounds['y'][0]+2, self.scene_bounds['y'][1]-2)
            z = random.uniform(self.scene_bounds['z'][0]+5, self.scene_bounds['z'][1]-5)
            if np.linalg.norm(np.array([x, y, z]) - np.array(ppos)) > 10:
                break
        p0 = np.array([x, y, z], dtype=np.float32)
        p3 = np.array(ppos, dtype=np.float32)
        # Dois pontos de controle intermediários aleatórios (entre p0 e p3)
        def random_ctrl(p0, p3, spread=8):
            v = p3 - p0
            t = random.uniform(0.25, 0.75)
            base = p0 + v * t
            offset = np.random.uniform(-spread, spread, 3)
            return base + offset
        p1 = random_ctrl(p0, p3)
        p2 = random_ctrl(p0, p3)
        self.asteroid_curve = [p0, p1, p2, p3]
        self.asteroid_target_planet = pname
        self.asteroid_target_planet_radius = pradius
        self.asteroid_target_planet_func = pfunc
        self.asteroid = {
            't': 0.0,
            'alive': True
        }

    def update(self):
        """Atualiza o estado da simulação"""
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time
        if not self.paused:
            self.elapsed_time += delta_time * self.simulation_speed
        # Atualizar asteroide automático
        if self.asteroid and self.asteroid.get('alive', False):
            # Atualizar ponto final da curva para seguir planeta alvo
            pname = self.asteroid_target_planet
            pfunc = self.asteroid_target_planet_func
            pradius = self.asteroid_target_planet_radius
            tnow = self.elapsed_time
            if pname == 'mars':
                p3 = pfunc(tnow)
                if isinstance(p3, np.ndarray):
                    p3 = p3.tolist()
            else:
                p3 = pfunc(tnow)
            p3 = np.array(p3, dtype=np.float32)
            # Atualizar curva: p0, p1, p2 mantêm, p3 muda
            self.asteroid_curve[3] = p3
            # Avançar t
            self.asteroid['t'] += self.asteroid_speed * delta_time * self.simulation_speed
            tval = min(self.asteroid['t'], 1.0)
            pos = self.bezier_cubic(tval, *self.asteroid_curve)
            self.asteroid['pos'] = pos.tolist()
            # Testar colisão com planeta alvo
            planet_sphere = Sphere(p3.tolist(), pradius)
            asteroid_sphere = Sphere(pos.tolist(), self.asteroid_radius)
            if sphere_sphere_collision(asteroid_sphere, planet_sphere):
                self.asteroid['alive'] = False
                print(f"Colisão: Asteroide colidiu com {pname.upper()}!")
                self.show_warning(f"Asteroide colidiu com {pname.upper()}!")
            # Se chegou ao final da curva sem colidir, remove também
            elif self.asteroid['t'] >= 1.0:
                self.asteroid['alive'] = False
        # Testar colisão do asteroide com planetas
        if self.asteroid and self.asteroid.get('alive', False):
            asteroid_sphere = Sphere(self.asteroid['pos'], self.asteroid_radius)
            # Lista de planetas (nome, posição, raio)
            planets = []
            # Mercúrio
            mercury_orbit = 48 * self.elapsed_time
            mercury_pos = [
                8 * math.cos(math.radians(mercury_orbit)),
                0,
                8 * math.sin(math.radians(mercury_orbit))
            ]
            planets.append(('mercury', mercury_pos, 0.38))
            # Vênus
            venus_orbit = 35 * self.elapsed_time
            venus_pos = [
                10 * math.cos(math.radians(venus_orbit)),
                0,
                10 * math.sin(math.radians(venus_orbit))
            ]
            planets.append(('venus', venus_pos, 0.95))
            # Terra
            earth_orbit = 29 * self.elapsed_time
            earth_pos = [
                14 * math.cos(math.radians(earth_orbit)),
                0,
                14 * math.sin(math.radians(earth_orbit))
            ]
            planets.append(('earth', earth_pos, 1.0))
            # Marte (agora órbita circular)
            mars_orbit = 24 * self.elapsed_time
            mars_pos = [
                18 * math.cos(math.radians(mars_orbit)),
                0,
                18 * math.sin(math.radians(mars_orbit))
            ]
            planets.append(('mars', mars_pos, 0.53))
            # Júpiter
            jupiter_orbit = 13 * self.elapsed_time
            jupiter_pos = [
                25 * math.cos(math.radians(jupiter_orbit)),
                0,
                25 * math.sin(math.radians(jupiter_orbit))
            ]
            planets.append(('jupiter', jupiter_pos, 3.0))
            # Saturno
            saturn_orbit = 9 * self.elapsed_time
            saturn_pos = [
                32 * math.cos(math.radians(saturn_orbit)),
                0,
                32 * math.sin(math.radians(saturn_orbit))
            ]
            planets.append(('saturn', saturn_pos, 2.5))
            # Sol (não pode colidir)
            sun_pos = [0, 0, 0]
            sun_radius = 5.0
            # Teste: se asteroide está dentro do sol, empurra para fora
            dist_to_sun = np.linalg.norm(np.array(self.asteroid['pos']) - np.array(sun_pos))
            if dist_to_sun < sun_radius + self.asteroid_radius:
                # Empurra para fora do sol
                direction = np.array(self.asteroid['pos']) - np.array(sun_pos)
                if np.linalg.norm(direction) == 0:
                    direction = np.array([1, 0, 0])
                direction = direction / np.linalg.norm(direction)
                self.asteroid['pos'] = (np.array(sun_pos) + direction * (sun_radius + self.asteroid_radius + 0.1)).tolist()
            # Testa colisão com planetas (exceto sol)
            for pname, ppos, pradius in planets:
                planet_sphere = Sphere(ppos, pradius)
                if sphere_sphere_collision(asteroid_sphere, planet_sphere):
                    self.asteroid['alive'] = False
                    print(f"Colisão: Asteroide colidiu com {pname.upper()}!")
                    # Exibe aviso na tela (pygame)
                    self.show_warning(f"Asteroide colidiu com {pname.upper()}!")
                    break
            # Testa colisão com paredes (AABB)
            asteroid_aabb = create_aabb_for_object(self.asteroid['pos'], [self.asteroid_radius*2]*3)
            scene_aabb = AABB(
                [self.scene_bounds['x'][0], self.scene_bounds['y'][0], self.scene_bounds['z'][0]],
                [self.scene_bounds['x'][1], self.scene_bounds['y'][1], self.scene_bounds['z'][1]]
            )
            if not aabb_aabb_collision(asteroid_aabb, scene_aabb):
                # Fora da cena, ajusta para dentro
                pos = np.array(self.asteroid['pos'])
                for i, axis in enumerate(['x', 'y', 'z']):
                    minb, maxb = self.scene_bounds[axis]
                    if pos[i] - self.asteroid_radius < minb:
                        pos[i] = minb + self.asteroid_radius
                    if pos[i] + self.asteroid_radius > maxb:
                        pos[i] = maxb - self.asteroid_radius
                self.asteroid['pos'] = pos.tolist()
    
    def show_warning(self, text):
        """Exibe um aviso na tela por alguns segundos"""
        font = pygame.font.SysFont("Arial", 36, bold=True)
        surface = font.render(text, True, (255, 80, 80))
        self.screen.blit(surface, (self.width//2 - surface.get_width()//2, 40))
        pygame.display.flip()
        pygame.time.wait(1200)  # 1.2 segundos

    def create_sphere_mesh(self, radius, slices, stacks):
        """Cria a malha para uma esfera com coordenadas de textura"""
        vertices = []
        normals = []
        texcoords = []
        indices = []
        for i in range(stacks + 1):
            lat = math.pi * i / stacks
            v = i / stacks
            for j in range(slices + 1):
                lon = 2 * math.pi * j / slices
                u = j / slices
                x = radius * math.sin(lat) * math.cos(lon)
                y = radius * math.cos(lat)
                z = radius * math.sin(lat) * math.sin(lon)
                vertices.extend([x, y, z])
                normals.extend([math.sin(lat) * math.cos(lon), math.cos(lat), math.sin(lat) * math.sin(lon)])
                texcoords.extend([u, 1 - v])
        for i in range(stacks):
            for j in range(slices):
                first = i * (slices + 1) + j
                second = first + slices + 1
                indices.extend([first, second, first + 1])
                indices.extend([second, second + 1, first + 1])
        vertices = np.array(vertices, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        texcoords = np.array(texcoords, dtype=np.float32)
        indices = np.array(indices, dtype=np.uint32)
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        nbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, nbo)
        glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)
        tbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, tbo)
        glBufferData(GL_ARRAY_BUFFER, texcoords.nbytes, texcoords, GL_STATIC_DRAW)
        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
        glBindVertexArray(0)
        return vao, vbo, nbo, tbo, ebo, len(indices)

    def draw_sphere_shader(self, program, position, scale=1.0, texture=None):
        gl.glUseProgram(program)
        model = np.identity(4, dtype=np.float32)
        model[:3, 3] = position
        model[:3, :3] *= scale
        loc_model = gl.glGetUniformLocation(program, "model")
        loc_view = gl.glGetUniformLocation(program, "view")
        loc_proj = gl.glGetUniformLocation(program, "projection")
        loc_light = gl.glGetUniformLocation(program, "lightPos")
        loc_viewpos = gl.glGetUniformLocation(program, "viewPos")
        gl.glUniformMatrix4fv(loc_model, 1, gl.GL_TRUE, model)
        gl.glUniformMatrix4fv(loc_view, 1, gl.GL_TRUE, self.create_view_matrix())
        gl.glUniformMatrix4fv(loc_proj, 1, gl.GL_TRUE, self.create_projection_matrix())
        gl.glUniform3f(loc_light, 0, 0, 0)
        cam_pos = self.get_orbit_camera_position() if self.camera_type == "orbit" else np.array(self.camera_position)
        gl.glUniform3f(loc_viewpos, *cam_pos)
        # Bind texture if provided
        if texture is not None:
            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
            tex_loc = gl.glGetUniformLocation(program, "tex")
            if tex_loc != -1:
                gl.glUniform1i(tex_loc, 0)
        gl.glBindVertexArray(self.sphere_vao)
        pos_loc = gl.glGetAttribLocation(program, "position")
        norm_loc = gl.glGetAttribLocation(program, "normal")
        tex_loc = gl.glGetAttribLocation(program, "texcoord")
        # VBO posição
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.sphere_vbo)
        gl.glEnableVertexAttribArray(pos_loc)
        gl.glVertexAttribPointer(pos_loc, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        # VBO normal
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.sphere_nbo)
        gl.glEnableVertexAttribArray(norm_loc)
        gl.glVertexAttribPointer(norm_loc, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        # VBO texcoord
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.sphere_tbo)
        gl.glEnableVertexAttribArray(tex_loc)
        gl.glVertexAttribPointer(tex_loc, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        # EBO
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.sphere_ebo)
        gl.glDrawElements(gl.GL_TRIANGLES, self.sphere_index_count, gl.GL_UNSIGNED_INT, None)
        gl.glDisableVertexAttribArray(pos_loc)
        gl.glDisableVertexAttribArray(norm_loc)
        gl.glDisableVertexAttribArray(tex_loc)
        gl.glBindVertexArray(0)
        if texture is not None:
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        gl.glUseProgram(0)

    def draw_scene(self):
        """Desenha toda a cena"""
        # Limpar buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Resetar matriz de modelview
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Configurar câmera
        self.setup_camera()
        
        # Atualizar posição da luz para o sol
        glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, 0, 1])
        
        # Desenhar skybox
        self.draw_skybox()
        
        # Desenhar sol
        self.draw_sun()
        
        # Desenhar planetas usando curvas de Bézier para as órbitas e cálculos baseados em tempo
        # Cada planeta tem seu período orbital e rotacional baseado em dados reais (simplificados)
        
        # Mercúrio (Gouraud + textura)
        mercury_orbit = 48 * self.elapsed_time
        mercury_rotation = 10 * self.elapsed_time
        mercury_x = 8 * math.cos(math.radians(mercury_orbit))
        mercury_z = 8 * math.sin(math.radians(mercury_orbit))
        if self.show_orbits:
            self.draw_orbit(8)
        self.draw_sphere_shader(self.gouraud_prog, position=[mercury_x, 0, mercury_z], scale=0.38, texture=self.textures['mercury'])

        # Vênus (Gouraud + textura)
        venus_orbit = 35 * self.elapsed_time
        venus_rotation = 8 * self.elapsed_time
        venus_x = 10 * math.cos(math.radians(venus_orbit))
        venus_z = 10 * math.sin(math.radians(venus_orbit))
        if self.show_orbits:
            self.draw_orbit(10)
        self.draw_sphere_shader(self.gouraud_prog, position=[venus_x, 0, venus_z], scale=0.95, texture=self.textures['venus'])

        # Terra (Gouraud + textura)
        earth_orbit = 29 * self.elapsed_time
        earth_rotation = 365 * self.elapsed_time
        earth_x = 14 * math.cos(math.radians(earth_orbit))
        earth_z = 14 * math.sin(math.radians(earth_orbit))
        if self.show_orbits:
            self.draw_orbit(14)
        self.draw_sphere_shader(self.gouraud_prog, position=[earth_x, 0, earth_z], scale=1.0, texture=self.textures['earth'])

        # Lua (orbita ao redor da Terra)
        glPushMatrix()
        glTranslatef(earth_x, 0, earth_z)
        moon_orbit = 10 * self.elapsed_time
        moon_rotation = 10 * self.elapsed_time
        moon_x = 2.5 * math.cos(math.radians(moon_orbit))
        moon_z = 2.5 * math.sin(math.radians(moon_orbit))
        glTranslatef(moon_x, 0, moon_z)
        glRotatef(moon_rotation, 0, 1, 0)
        glBindTexture(GL_TEXTURE_2D, self.textures['moon'])
        glEnable(GL_TEXTURE_2D)
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, 0.27, 16, 16)
        gluDeleteQuadric(quadric)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()

        # Marte (Gouraud + textura)
        mars_orbit = 24 * self.elapsed_time
        mars_rotation = 350 * self.elapsed_time
        mars_x = 18 * math.cos(math.radians(mars_orbit))
        mars_z = 18 * math.sin(math.radians(mars_orbit))
        if self.show_orbits:
            self.draw_orbit(18)
        self.draw_sphere_shader(self.gouraud_prog, position=[mars_x, 0, mars_z], scale=0.53, texture=self.textures['mars'])

        # Júpiter (Gouraud + textura)
        jupiter_orbit = 13 * self.elapsed_time
        jupiter_rotation = 870 * self.elapsed_time
        jupiter_x = 25 * math.cos(math.radians(jupiter_orbit))
        jupiter_z = 25 * math.sin(math.radians(jupiter_orbit))
        if self.show_orbits:
            self.draw_orbit(25)
        self.draw_sphere_shader(self.gouraud_prog, position=[jupiter_x, 0, jupiter_z], scale=3.0, texture=self.textures['jupiter'])

        # Saturno (Gouraud + textura)
        saturn_orbit = 9 * self.elapsed_time
        saturn_rotation = 820 * self.elapsed_time
        saturn_x = 32 * math.cos(math.radians(saturn_orbit))
        saturn_z = 32 * math.sin(math.radians(saturn_orbit))
        if self.show_orbits:
            self.draw_orbit(32)
        self.draw_sphere_shader(self.gouraud_prog, position=[saturn_x, 0, saturn_z], scale=2.5, texture=self.textures['saturn'])

        # Anéis de Saturno
        glPushMatrix()
        glTranslatef(saturn_x, 0, saturn_z)
        glRotatef(80, 1, 0, 0)
        glDisable(GL_LIGHTING)
        glColor4f(1.0, 1.0, 0.8, 0.7)
        inner_radius = 3.0
        outer_radius = 5.0
        quadric = gluNewQuadric()
        gluDisk(quadric, inner_radius, outer_radius, 32, 4)
        gluDeleteQuadric(quadric)
        glEnable(GL_LIGHTING)
        glPopMatrix()

        # Asteroide (mantém como estava)
        if self.asteroid and self.asteroid.get('alive', False):
            glPushMatrix()
            glTranslatef(*self.asteroid['pos'])
            glBindTexture(GL_TEXTURE_2D, self.textures['asteroid'])
            glEnable(GL_TEXTURE_2D)
            quadric = gluNewQuadric()
            gluQuadricTexture(quadric, GL_TRUE)
            gluSphere(quadric, self.asteroid_radius, 16, 16)
            gluDeleteQuadric(quadric)
            glDisable(GL_TEXTURE_2D)
            glPopMatrix()
            self.draw_bezier_orbit(self.asteroid_curve, steps=100)
    
    def setup_camera(self):
        """Configura a câmera com base no modo atual"""
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # Corrigir: passar matriz transposta
        glLoadMatrixf(self.create_view_matrix().T.astype(np.float32))

    # Adicionar o método run() que serve como ponto de entrada principal
    def run(self):
        """Loop principal do programa"""
        running = True
        
        while running:
            # Processar eventos do usuário
            running = self.handle_events()
            
            # Atualizar lógica da simulação
            self.update()
            
            # Renderizar cena
            self.draw_scene()
            
            # Atualizar tela
            pygame.display.flip()
            pygame.time.wait(10)  # Limitar FPS
        
        pygame.quit()

    def bezier_cubic(self, t, p0, p1, p2, p3):
        """Calcula ponto na curva de Bézier cúbica"""
        return (
            (1 - t) ** 3 * p0 +
            3 * (1 - t) ** 2 * t * p1 +
            3 * (1 - t) * t ** 2 * p2 +
            t ** 3 * p3
        )

    def draw_bezier_orbit(self, points, steps=100):
        """Desenha a curva de Bézier como órbita"""
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        glColor3f(1.0, 0.5, 0.2)  # Laranja para destacar
        glBegin(GL_LINE_STRIP)
        for i in range(steps + 1):
            t = i / steps
            pos = self.bezier_cubic(t, *points)
            glVertex3f(pos[0], pos[1], pos[2])
        glEnd()
        glEnable(GL_LIGHTING)