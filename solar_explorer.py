import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import time
import random
import os

# Importar os módulos que criamos
from collisions import *
from shaders import init_shaders
from model_loader import load_obj_model

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
        gluPerspective(45, (width / height), 0.1, 100.0)
        
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
        self.camera_position = [0, 0, 30]  # Para câmera livre
        
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
        self.delta_time = 0  # Adicionar esta linha
        
        # Criar diretório de modelos se não existir
        if not os.path.exists("models"):
            os.makedirs("models")
            print("Pasta de modelos criada: models/")

        # Inicialização dos shaders
        self.shader_programs = init_shaders()
        
        # Carregar modelos 3D complexos
        self.models = {}
        self.load_models()
        
        # Meteoros/asteroides
        self.asteroids = []
        self.asteroid_spawn_timer = 1.0
    
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
            'stars': 'textures/stars.jpg'
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
        """Desenha o fundo estrelado como um domo"""
        glDisable(GL_LIGHTING)  # Desativar iluminação para o céu
        
        glBindTexture(GL_TEXTURE_2D, self.textures['stars'])
        glEnable(GL_TEXTURE_2D)
        
        # Salvar matriz atual
        glPushMatrix()
        
        # Inverter as normais para desenhar por dentro
        glFrontFace(GL_CW)
        
        # Desenhar esfera para o céu
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, 90.0, 32, 32)
        gluDeleteQuadric(quadric)
        
        # Restaurar orientação das normais
        glFrontFace(GL_CCW)
        
        glPopMatrix()
        
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)  # Reativar iluminação
    
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
        
        # Mercúrio
        mercury_orbit = 48 * self.elapsed_time  # 48 graus por segundo (período orbital de 7.5 segundos)
        mercury_rotation = 10 * self.elapsed_time  # Rotação própria
        self.draw_planet('mercury', 0.38, 8, mercury_orbit, mercury_rotation)
        
        # Vênus
        venus_orbit = 35 * self.elapsed_time  # Mais lento que Mercúrio
        venus_rotation = 8 * self.elapsed_time  # Rotação própria
        self.draw_planet('venus', 0.95, 10, venus_orbit, venus_rotation)
        
        # Terra e Lua
        earth_orbit = 29 * self.elapsed_time  # Período orbital
        earth_rotation = 365 * self.elapsed_time  # Rotação própria (1 dia = 1 grau)
        earth_pos = self.draw_planet('earth', 1.0, 14, earth_orbit, earth_rotation)
        
        # Lua (orbita ao redor da Terra)
        glPushMatrix()
        glTranslatef(earth_pos[0], earth_pos[1], earth_pos[2])
        
        moon_orbit = 10 * self.elapsed_time  # Período orbital rápido ao redor da Terra
        moon_rotation = 10 * self.elapsed_time  # Rotação da lua
        
        # Posição da lua na órbita ao redor da Terra
        moon_x = 2.5 * math.cos(math.radians(moon_orbit))
        moon_z = 2.5 * math.sin(math.radians(moon_orbit))
        
        glTranslatef(moon_x, 0, moon_z)
        glRotatef(moon_rotation, 0, 1, 0)
        
        # Desenhar lua
        glBindTexture(GL_TEXTURE_2D, self.textures['moon'])
        glEnable(GL_TEXTURE_2D)
        
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, 0.27, 16, 16)
        gluDeleteQuadric(quadric)
        
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
        
        # Marte
        mars_orbit = 24 * self.elapsed_time
        mars_rotation = 350 * self.elapsed_time
        self.draw_planet('mars', 0.53, 16, mars_orbit, mars_rotation)
        
        # Júpiter
        jupiter_orbit = 13 * self.elapsed_time
        jupiter_rotation = 870 * self.elapsed_time
        self.draw_planet('jupiter', 3.0, 25, jupiter_orbit, jupiter_rotation)
        
        # Saturno
        saturn_orbit = 9 * self.elapsed_time
        saturn_rotation = 820 * self.elapsed_time
        saturn_pos = self.draw_planet('saturn', 2.5, 32, saturn_orbit, saturn_rotation)
        
        # Anéis de Saturno
        glPushMatrix()
        glTranslatef(saturn_pos[0], saturn_pos[1], saturn_pos[2])
        glRotatef(80, 1, 0, 0)  # Inclinar os anéis
        
        # Desenhar anéis como um disco fino
        glDisable(GL_LIGHTING)
        glColor4f(1.0, 1.0, 0.8, 0.7)
        
        inner_radius = 3.0  # Raio interno dos anéis
        outer_radius = 5.0  # Raio externo dos anéis
        
        quadric = gluNewQuadric()
        gluDisk(quadric, inner_radius, outer_radius, 32, 4)
        gluDeleteQuadric(quadric)
        
        glEnable(GL_LIGHTING)
        glPopMatrix()
    
    def setup_camera(self):
        """Configura a câmera baseada no modo atual"""
        if self.camera_type == "orbit":
            # Câmera orbital - gira ao redor de um ponto central
            # Convertendo para radianos para cálculos
            h_rad = math.radians(self.camera_rotation_h)
            v_rad = math.radians(self.camera_rotation_v)
            
            # Calcular posição da câmera em coordenadas esféricas
            x = self.camera_distance * math.cos(v_rad) * math.sin(h_rad)
            y = self.camera_distance * math.sin(v_rad)
            z = self.camera_distance * math.cos(v_rad) * math.cos(h_rad)
            
            # Configurar câmera olhando para o centro
            gluLookAt(x, y, z, 0, 0, 0, 0, 1, 0)
        else:
            # Câmera livre - pode mover em qualquer direção
            # Esta é uma implementação básica, pode ser expandida
            gluLookAt(
                self.camera_position[0], self.camera_position[1], self.camera_position[2],
                0, 0, 0,  # Olhando para o centro
                0, 1, 0   # Vetor "para cima"
            )
    
    def handle_events(self):
        """Processa eventos do usuário"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                self.keys.add(event.key)
                
                # Tecla ESC para sair
                if event.key == pygame.K_ESCAPE:
                    return False
                
                # C para alternar tipo de câmera
                elif event.key == pygame.K_c:
                    self.camera_type = "free" if self.camera_type == "orbit" else "orbit"
                    print(f"Câmera alterada para: {self.camera_type}")
                
                # Pausar/continuar simulação
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                    print("Simulação " + ("pausada" if self.paused else "continuada"))
                
                # Alternar visualização de órbitas
                elif event.key == pygame.K_o:
                    self.show_orbits = not self.show_orbits
                
                # Ajustar velocidade da simulação
                elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS):
                    self.simulation_speed *= 1.5
                    print(f"Velocidade: {self.simulation_speed:.1f}x")
                
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.simulation_speed /= 1.5
                    print(f"Velocidade: {self.simulation_speed:.1f}x")
            
            elif event.type == pygame.KEYUP:
                if event.key in self.keys:
                    self.keys.remove(event.key)
            
            # Controle do mouse para rotação da câmera
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo
                    self.last_mouse_pos = event.pos
                
                # Controle de zoom com roda do mouse
                elif event.button == 4:  # Roda para cima
                    self.camera_distance = max(5.0, self.camera_distance - 1.0)
                elif event.button == 5:  # Roda para baixo
                    self.camera_distance = min(60.0, self.camera_distance + 1.0)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Botão esquerdo
                    self.last_mouse_pos = None
            
            elif event.type == pygame.MOUSEMOTION and self.last_mouse_pos:
                # Calcular o deslocamento do mouse
                dx = event.pos[0] - self.last_mouse_pos[0]
                dy = event.pos[1] - self.last_mouse_pos[1]
                self.last_mouse_pos = event.pos
                
                # Sensibilidade do mouse
                sensitivity = 0.3
                
                if self.camera_type == "orbit":
                    # Rotação horizontal da câmera orbital
                    self.camera_rotation_h += dx * sensitivity
                    # Rotação vertical da câmera orbital (com limites)
                    self.camera_rotation_v = max(-85, min(85, self.camera_rotation_v - dy * sensitivity))
                else:
                    # Para câmera livre, implementaríamos rotação da direção
                    pass
        
        # Processar teclas pressionadas continuamente
        self.process_keyboard()
        
        return True
    
    def process_keyboard(self):
        """Processa entradas contínuas do teclado"""
        # Movimento da câmera livre
        if self.camera_type == "free":
            speed = 0.2
            
            # Frente/trás
            if pygame.K_w in self.keys:
                self.camera_position[2] -= speed
            if pygame.K_s in self.keys:
                self.camera_position[2] += speed
            
            # Esquerda/direita
            if pygame.K_a in self.keys:
                self.camera_position[0] -= speed
            if pygame.K_d in self.keys:
                self.camera_position[0] += speed
            
            # Cima/baixo
            if pygame.K_SPACE in self.keys:
                self.camera_position[1] += speed
            if pygame.K_LSHIFT in self.keys:
                self.camera_position[1] -= speed
    
    def load_models(self):
        """Carrega modelos 3D para uso na cena"""
        # Tentar carregar modelo de asteroide
        try:
            self.models["asteroid"] = load_obj_model("models/asteroid.obj")
        except:
            print("Modelo de asteroide não encontrado, usando esfera simplificada.")
            self.models["asteroid"] = None  # Usaremos primitiva GLU
    
    def create_cube_model(self):
        """Cria um modelo de cubo simples como fallback"""
        # Criar e configurar um VAO
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)
        
        # Vértices, normais e coords de textura do cubo
        vertices = np.array([
            # Frente
            -0.5, -0.5,  0.5,   0.0,  0.0,  1.0,   0.0, 0.0,
             0.5, -0.5,  0.5,   0.0,  0.0,  1.0,   1.0, 0.0,
             0.5,  0.5,  0.5,   0.0,  0.0,  1.0,   1.0, 1.0,
            -0.5,  0.5,  0.5,   0.0,  0.0,  1.0,   0.0, 1.0,
            # Trás
            -0.5, -0.5, -0.5,   0.0,  0.0, -1.0,   1.0, 0.0,
             0.5, -0.5, -0.5,   0.0,  0.0, -1.0,   0.0, 0.0,
             0.5,  0.5, -0.5,   0.0,  0.0, -1.0,   0.0, 1.0,
            -0.5,  0.5, -0.5,   0.0,  0.0, -1.0,   1.0, 1.0,
            # ...existing code... (outros lados do cubo)
        ], dtype=np.float32)
        
        # Índices para os triângulos
        indices = np.array([
            0, 1, 2, 0, 2, 3,    # Frente
            4, 5, 6, 4, 6, 7,    # Trás
            # ...existing code... (outros triângulos)
        ], dtype=np.uint32)
        
        # Criar e configurar VBO para os vértices
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)
        
        # Configurar atributos de vértice
        stride = 8 * 4  # 8 floats por vértice (x,y,z, nx,ny,nz, u,v)
        
        # Posição
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, None)
        glEnableVertexAttribArray(0)
        
        # Normal
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))
        glEnableVertexAttribArray(1)
        
        # Texcoord
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6 * 4))
        glEnableVertexAttribArray(2)
        
        # Elemento buffer
        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices, GL_STATIC_DRAW)
        
        # Desligar VAO
        glBindVertexArray(0)
        
        return vao, len(indices)
    
    def spawn_asteroid(self):
        """Cria um novo asteroide em uma posição aleatória"""
        # Escolher uma posição aleatória na esfera externa
        phi = random.uniform(0, 2 * math.pi)
        theta = random.uniform(-math.pi/4, math.pi/4)  # Limitar altura
        
        # Raio da esfera de spawn
        spawn_radius = 60.0
        
        # Posição inicial
        x = spawn_radius * math.cos(theta) * math.cos(phi)
        y = spawn_radius * math.sin(theta)
        z = spawn_radius * math.cos(theta) * math.sin(phi)
        
        # Velocidade em direção a um ponto aleatório dentro do sistema
        target_radius = random.uniform(0, 25)  # Alvo dentro do sistema
        target_angle = random.uniform(0, 2 * math.pi)
        target_x = target_radius * math.cos(target_angle)
        target_z = target_radius * math.sin(target_angle)
        
        # Vetor direção da velocidade
        direction = np.array([target_x - x, -y, target_z - z])
        direction = direction / np.linalg.norm(direction)
        
        # Velocidade aleatória
        speed = random.uniform(3.0, 8.0)
        velocity = direction * speed
        
        # Criar o asteroide
        asteroid = {
            "position": np.array([x, y, z]),
            "velocity": velocity,
            "rotation": np.array([random.uniform(0, 360) for _ in range(3)]),
            "rotation_speed": np.array([random.uniform(-30, 30) for _ in range(3)]),
            "scale": random.uniform(0.2, 0.5),
            "active": True
        }
        
        # Adicionar colisor
        asteroid["collider"] = Sphere(asteroid["position"], asteroid["scale"])
        
        self.asteroids.append(asteroid)
    
    # Modificar a função update para incluir colisões
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
            
            # Atualizar asteroides e verificar colisões
            self.asteroid_spawn_timer -= self.delta_time
            if self.asteroid_spawn_timer <= 0:
                self.spawn_asteroid()
                self.asteroid_spawn_timer = random.uniform(3.0, 8.0)
            
            # Atualizar posições dos asteroides
            for asteroid in self.asteroids:
                if not asteroid["active"]:
                    continue
                
                # Atualizar posição
                asteroid["position"] += asteroid["velocity"] * self.delta_time
                
                # Atualizar rotação
                asteroid["rotation"] += asteroid["rotation_speed"] * self.delta_time
                
                # Atualizar colisor
                asteroid["collider"].center = asteroid["position"]
                
                # Verificar se está muito longe ou atingiu o sol
                if np.linalg.norm(asteroid["position"]) > 100.0:
                    asteroid["active"] = False
                
                # Colisão com o Sol
                sun_sphere = Sphere(np.array([0, 0, 0]), 5.0)  # Sol tem raio 5
                if sphere_sphere_collision(asteroid["collider"], sun_sphere):
                    asteroid["active"] = False
                    print("Asteroide atingiu o Sol!")
                
                # Colisão com planetas
                earth_pos = np.array([
                    14 * math.cos(math.radians(29 * self.elapsed_time)),
                    0,
                    14 * math.sin(math.radians(29 * self.elapsed_time))
                ])
                earth_sphere = Sphere(earth_pos, 1.0)
                if sphere_sphere_collision(asteroid["collider"], earth_sphere):
                    asteroid["active"] = False
                    print("Asteroide atingiu a Terra!")
            
            # Remover asteroides inativos
            self.asteroids = [a for a in self.asteroids if a["active"]]
    
    # Adicionar à função draw_scene para renderizar modelos 3D e asteroides
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
        
        # Mercúrio
        mercury_orbit = 48 * self.elapsed_time  # 48 graus por segundo (período orbital de 7.5 segundos)
        mercury_rotation = 10 * self.elapsed_time  # Rotação própria
        self.draw_planet('mercury', 0.38, 8, mercury_orbit, mercury_rotation)
        
        # Vênus
        venus_orbit = 35 * self.elapsed_time  # Mais lento que Mercúrio
        venus_rotation = 8 * self.elapsed_time  # Rotação própria
        self.draw_planet('venus', 0.95, 10, venus_orbit, venus_rotation)
        
        # Terra e Lua
        earth_orbit = 29 * self.elapsed_time  # Período orbital
        earth_rotation = 365 * self.elapsed_time  # Rotação própria (1 dia = 1 grau)
        earth_pos = self.draw_planet('earth', 1.0, 14, earth_orbit, earth_rotation)
        
        # Lua (orbita ao redor da Terra)
        glPushMatrix()
        glTranslatef(earth_pos[0], earth_pos[1], earth_pos[2])
        
        moon_orbit = 10 * self.elapsed_time  # Período orbital rápido ao redor da Terra
        moon_rotation = 10 * self.elapsed_time  # Rotação da lua
        
        # Posição da lua na órbita ao redor da Terra
        moon_x = 2.5 * math.cos(math.radians(moon_orbit))
        moon_z = 2.5 * math.sin(math.radians(moon_orbit))
        
        glTranslatef(moon_x, 0, moon_z)
        glRotatef(moon_rotation, 0, 1, 0)
        
        # Desenhar lua
        glBindTexture(GL_TEXTURE_2D, self.textures['moon'])
        glEnable(GL_TEXTURE_2D)
        
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, 0.27, 16, 16)
        gluDeleteQuadric(quadric)
        
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
        
        # Marte
        mars_orbit = 24 * self.elapsed_time
        mars_rotation = 350 * self.elapsed_time
        self.draw_planet('mars', 0.53, 16, mars_orbit, mars_rotation)
        
        # Júpiter
        jupiter_orbit = 13 * self.elapsed_time
        jupiter_rotation = 870 * self.elapsed_time
        self.draw_planet('jupiter', 3.0, 25, jupiter_orbit, jupiter_rotation)
        
        # Saturno
        saturn_orbit = 9 * self.elapsed_time
        saturn_rotation = 820 * self.elapsed_time
        saturn_pos = self.draw_planet('saturn', 2.5, 32, saturn_orbit, saturn_rotation)
        
        # Anéis de Saturno
        glPushMatrix()
        glTranslatef(saturn_pos[0], saturn_pos[1], saturn_pos[2])
        glRotatef(80, 1, 0, 0)  # Inclinar os anéis
        
        # Desenhar anéis como um disco fino
        glDisable(GL_LIGHTING)
        glColor4f(1.0, 1.0, 0.8, 0.7)
        
        inner_radius = 3.0  # Raio interno dos anéis
        outer_radius = 5.0  # Raio externo dos anéis
        
        quadric = gluNewQuadric()
        gluDisk(quadric, inner_radius, outer_radius, 32, 4)
        gluDeleteQuadric(quadric)
        
        glEnable(GL_LIGHTING)
        glPopMatrix()
        
        # Desenhar asteroides
        self.draw_asteroids()
    
    
    def draw_asteroids(self):
        """Desenha os asteroides"""
        for asteroid in self.asteroids:
            if not asteroid["active"]:
                continue
                
            # Matriz de modelo para o asteroide
            model_matrix = np.identity(4, dtype=np.float32)
            
            # Translação
            model_matrix[0, 3] = asteroid["position"][0]
            model_matrix[1, 3] = asteroid["position"][1]
            model_matrix[2, 3] = asteroid["position"][2]
            
            # Rotação em 3 eixos
            for axis in range(3):
                angle_rad = math.radians(asteroid["rotation"][axis])
                cos_a = math.cos(angle_rad)
                sin_a = math.sin(angle_rad)
                
                rotation = np.identity(4, dtype=np.float32)
                if axis == 0:  # X
                    rotation[1, 1] = cos_a
                    rotation[1, 2] = -sin_a
                    rotation[2, 1] = sin_a
                    rotation[2, 2] = cos_a
                elif axis == 1:  # Y
                    rotation[0, 0] = cos_a
                    rotation[0, 2] = sin_a
                    rotation[2, 0] = -sin_a
                    rotation[2, 2] = cos_a
                else:  # Z
                    rotation[0, 0] = cos_a
                    rotation[0, 1] = -sin_a
                    rotation[1, 0] = sin_a
                    rotation[1, 1] = cos_a
                
                model_matrix = np.matmul(model_matrix, rotation)
            
            # Escala
            model_matrix[0, 0] *= asteroid["scale"]
            model_matrix[1, 1] *= asteroid["scale"]
            model_matrix[2, 2] *= asteroid["scale"]
            
            # Matriz de visualização e projeção
            view_matrix = self.create_view_matrix()
            projection_matrix = self.create_projection_matrix()
            
            # Se tivermos shaders, usar o shader Gouraud para os asteroides
            if self.shader_programs and "gouraud" in self.shader_programs:
                shader = self.shader_programs["gouraud"]
                glUseProgram(shader)
                
                # Passar matrizes para o shader
                model_loc = glGetUniformLocation(shader, "model")
                view_loc = glGetUniformLocation(shader, "view")
                proj_loc = glGetUniformLocation(shader, "projection")
                
                glUniformMatrix4fv(model_loc, 1, GL_FALSE, model_matrix)
                glUniformMatrix4fv(view_loc, 1, GL_FALSE, view_matrix)
                glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection_matrix)
                
                # Configurar luz
                light_pos_loc = glGetUniformLocation(shader, "lightPos")
                view_pos_loc = glGetUniformLocation(shader, "viewPos")
                light_color_loc = glGetUniformLocation(shader, "lightColor")
                ambient_color_loc = glGetUniformLocation(shader, "ambientColor")
                shininess_loc = glGetUniformLocation(shader, "shininess")
                is_light_loc = glGetUniformLocation(shader, "isLightSource")
                
                # Posição da luz (sol)
                glUniform3f(light_pos_loc, 0.0, 0.0, 0.0)
                
                # Posição da câmera
                if self.camera_type == "orbit":
                    camera_pos = self.get_orbit_camera_position()
                    glUniform3f(view_pos_loc, camera_pos[0], camera_pos[1], camera_pos[2])
                else:
                    # Câmera livre
                    glUniform3f(view_pos_loc, 0.0, 0.0, 30.0)
                
                # Outras propriedades
                glUniform3f(light_color_loc, 1.0, 1.0, 0.9)
                glUniform3f(ambient_color_loc, 0.1, 0.1, 0.1)
                glUniform1f(shininess_loc, 16.0) # Menos brilhante que os planetas
                glUniform1i(is_light_loc, 0)
                
                # Textura do asteroide
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, self.textures["asteroid"])
                glUniform1i(glGetUniformLocation(shader, "textureMap"), 0)
                
                # Se tivermos o modelo 3D do asteroide, usá-lo
                if self.models.get("asteroid"):
                    vao, num_indices = self.models["asteroid"]
                    glBindVertexArray(vao)
                    glDrawElements(GL_TRIANGLES, num_indices, GL_UNSIGNED_INT, None)
                    glBindVertexArray(0)
                else:
                    # Caso contrário, desenhar uma esfera usando GLU
                    quadric = gluNewQuadric()
                    gluQuadricTexture(quadric, GL_TRUE)
                    gluSphere(quadric, 1.0, 16, 16) # A escala já está na matriz de modelo
                    gluDeleteQuadric(quadric)
                
                # Desligar shader
                glUseProgram(0)
            else:
                # Caso não tenhamos shaders, usar pipeline fixo do OpenGL
                glPushMatrix()
                glMultMatrixf(view_matrix)
                glMultMatrixf(model_matrix)
                
                # Desenhar o asteroide
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, self.textures["asteroid"])
                
                quadric = gluNewQuadric()
                gluQuadricTexture(quadric, GL_TRUE)
                gluSphere(quadric, 1.0, 12, 12)
                gluDeleteQuadric(quadric)
                
                glDisable(GL_TEXTURE_2D)
                glPopMatrix()
    
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

if __name__ == "__main__":
    explorer = SolarExplorer()
    explorer.run()
