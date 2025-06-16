"""
Carregador de modelos 3D no formato OBJ.

FONTE: Baseado no código do site "Real Python" (https://realpython.com/python-pyopengl/)
com adaptações para nossa aplicação específica.
"""

import numpy as np
from OpenGL.GL import *
import math
import random

class Model3D:
    def __init__(self, vertices=None, normals=None, texcoords=None, faces=None):
        self.vertices = vertices if vertices is not None else []
        self.normals = normals if normals is not None else []
        self.texcoords = texcoords if texcoords is not None else []
        self.faces = faces if faces is not None else []
        
        # Dados processados para OpenGL
        self.vertex_data = []
        self.normal_data = []
        self.texcoord_data = []
        self.index_data = []
        
        # OpenGL buffers
        self.vao = None
        self.vbo_vertices = None
        self.vbo_normals = None
        self.vbo_texcoords = None
        self.ebo = None
        self.num_indices = 0
        
        # Processamento inicial se dados foram fornecidos
        if len(self.faces) > 0:
            self.process_data()
    
    def process_data(self):
        """Processa os dados do modelo para uso no OpenGL"""
        # Criar arrays para os dados de vértices, normais e texcoords
        vertices_indexed = []
        normals_indexed = []
        texcoords_indexed = []
        indices = []
        
        index_map = {}  # Mapeia combinações v/vt/vn para índices
        next_index = 0
        
        for face in self.faces:
            face_indices = []
            
            for v in face:
                # Obter índices de vértice, normal e texcoord
                v_idx, t_idx, n_idx = v
                
                # Criar uma chave única para esta combinação
                key = (v_idx, t_idx, n_idx)
                
                # Verificar se essa combinação já existe
                if key not in index_map:
                    # Adicionar aos arrays
                    vertices_indexed.append(self.vertices[v_idx - 1])
                    
                    if n_idx > 0:
                        normals_indexed.append(self.normals[n_idx - 1])
                    else:
                        normals_indexed.append([0, 1, 0])  # Normal padrão
                    
                    if t_idx > 0:
                        texcoords_indexed.append(self.texcoords[t_idx - 1])
                    else:
                        texcoords_indexed.append([0, 0])  # Texcoord padrão
                    
                    # Registrar o novo índice
                    index_map[key] = next_index
                    next_index += 1
                
                # Adicionar o índice à face
                face_indices.append(index_map[key])
            
            # Triangulação básica de face (assumindo face convexa)
            for i in range(1, len(face_indices) - 1):
                indices.extend([face_indices[0], face_indices[i], face_indices[i + 1]])
        
        # Atribuir os dados processados
        self.vertex_data = np.array(vertices_indexed, dtype=np.float32)
        self.normal_data = np.array(normals_indexed, dtype=np.float32)
        self.texcoord_data = np.array(texcoords_indexed, dtype=np.float32)
        self.index_data = np.array(indices, dtype=np.uint32)
        
        print(f"Modelo processado: {len(vertices_indexed)} vértices, {len(indices)} índices")
    
    def setup_buffers(self):
        """Configura os buffers OpenGL para o modelo"""
        # Criar VAO
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        
        # VBO para vértices
        self.vbo_vertices = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glBufferData(GL_ARRAY_BUFFER, self.vertex_data, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)
        
        # VBO para normais
        self.vbo_normals = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_normals)
        glBufferData(GL_ARRAY_BUFFER, self.normal_data, GL_STATIC_DRAW)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(1)
        
        # VBO para coordenadas de textura
        self.vbo_texcoords = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_texcoords)
        glBufferData(GL_ARRAY_BUFFER, self.texcoord_data, GL_STATIC_DRAW)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(2)
        
        # EBO para índices
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.index_data, GL_STATIC_DRAW)
        
        # Armazenar número de índices
        self.num_indices = len(self.index_data)
        
        # Desligar VAO
        glBindVertexArray(0)
        
        return self.vao, self.num_indices

def parse_obj_file(file_path):
    """Carrega um modelo 3D a partir de um arquivo OBJ"""
    vertices = []
    normals = []
    texcoords = []
    faces = []
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith('#'):  # Comentário
                    continue
                
                values = line.split()
                if not values:
                    continue
                
                if values[0] == 'v':  # Vértice
                    vertices.append([float(x) for x in values[1:4]])
                elif values[0] == 'vn':  # Normal
                    normals.append([float(x) for x in values[1:4]])
                elif values[0] == 'vt':  # Texcoord
                    texcoords.append([float(x) for x in values[1:3]])
                elif values[0] == 'f':  # Face
                    face = []
                    for v in values[1:]:
                        w = v.split('/')
                        # Índice de vértice / texcoord / normal
                        # (OBS: índices em arquivos OBJ começam em 1)
                        face.append((
                            int(w[0]),
                            int(w[1]) if len(w) > 1 and w[1] else 0,
                            int(w[2]) if len(w) > 2 and w[2] else 0
                        ))
                    faces.append(face)
        
        print(f"Arquivo OBJ carregado: {file_path}")
        print(f"  Vértices: {len(vertices)}")
        print(f"  Normais: {len(normals)}")
        print(f"  Texcoords: {len(texcoords)}")
        print(f"  Faces: {len(faces)}")
        
        # Criar e retornar o modelo
        return Model3D(vertices, normals, texcoords, faces)
        
    except Exception as e:
        print(f"Erro ao carregar arquivo OBJ {file_path}: {e}")
        return None

def load_obj_model(file_path):
    """Carrega e configura um modelo OBJ para renderização"""
    try:
        model = parse_obj_file(file_path)
        if model:
            vao, num_indices = model.setup_buffers()
            return vao, num_indices
    except FileNotFoundError:
        print(f"Erro ao carregar arquivo OBJ {file_path}: Arquivo não encontrado")
    except Exception as e:
        print(f"Erro ao carregar arquivo OBJ {file_path}: {e}")
    
    print("Criando um modelo simples como fallback.")
    
    if "asteroid" in file_path.lower():
        return create_asteroid_model()
    else:
        return create_cube()

def create_cube():
    """Cria um cubo simples como fallback"""
    # Vértices do cubo
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
        # Esquerda
        -0.5, -0.5, -0.5,  -1.0,  0.0,  0.0,   0.0, 0.0,
        -0.5, -0.5,  0.5,  -1.0,  0.0,  0.0,   1.0, 0.0,
        -0.5,  0.5,  0.5,  -1.0,  0.0,  0.0,   1.0, 1.0,
        -0.5,  0.5, -0.5,  -1.0,  0.0,  0.0,   0.0, 1.0,
        # Direita
         0.5, -0.5, -0.5,   1.0,  0.0,  0.0,   1.0, 0.0,
         0.5, -0.5,  0.5,   1.0,  0.0,  0.0,   0.0, 0.0,
         0.5,  0.5,  0.5,   1.0,  0.0,  0.0,   0.0, 1.0,
         0.5,  0.5, -0.5,   1.0,  0.0,  0.0,   1.0, 1.0,
        # Cima
        -0.5,  0.5,  0.5,   0.0,  1.0,  0.0,   0.0, 0.0,
         0.5,  0.5,  0.5,   0.0,  1.0,  0.0,   1.0, 0.0,
         0.5,  0.5, -0.5,   0.0,  1.0,  0.0,   1.0, 1.0,
        -0.5,  0.5, -0.5,   0.0,  1.0,  0.0,   0.0, 1.0,
        # Baixo
        -0.5, -0.5,  0.5,   0.0, -1.0,  0.0,   0.0, 1.0,
         0.5, -0.5,  0.5,   0.0, -1.0,  0.0,   1.0, 1.0,
         0.5, -0.5, -0.5,   0.0, -1.0,  0.0,   1.0, 0.0,
        -0.5, -0.5, -0.5,   0.0, -1.0,  0.0,   0.0, 0.0
    ], dtype=np.float32)
    
    # Índices
    indices = np.array([
        0, 1, 2, 0, 2, 3,       # Frente
        4, 5, 6, 4, 6, 7,       # Trás
        8, 9, 10, 8, 10, 11,    # Esquerda
        12, 13, 14, 12, 14, 15, # Direita
        16, 17, 18, 16, 18, 19, # Cima
        20, 21, 22, 20, 22, 23  # Baixo
    ], dtype=np.uint32)
    
    # Configurar VAO
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    
    # VBO para todos os dados
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)
    
    # Configurar atributos de vértice
    stride = 8 * 4  # 8 floats por vértice (posição, normal, texcoord)
    
    # Posição (location 0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, None)
    glEnableVertexAttribArray(0)
    
    # Normal (location 1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))
    glEnableVertexAttribArray(1)
    
    # Texcoord (location 2)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6 * 4))
    glEnableVertexAttribArray(2)
    
    # EBO
    ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices, GL_STATIC_DRAW)
    
    # Desligar VAO
    glBindVertexArray(0)
    
    return vao, len(indices)

def create_asteroid_model():
    """Cria um modelo simples de asteroide irregular"""
    # Criar uma esfera e distorcer seus vértices para criar um asteroide irregular
    vertices = []
    normals = []
    texcoords = []
    
    # Parâmetros da esfera
    radius = 1.0
    stacks = 12
    slices = 12
    
    # Gerar vértices
    for i in range(stacks + 1):
        phi = math.pi * i / stacks
        for j in range(slices + 1):
            theta = 2 * math.pi * j / slices
            
            # Coordenadas esféricas para cartesianas
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.cos(phi)
            z = radius * math.sin(phi) * math.sin(theta)
            
            # Adicionar irregularidade
            distortion = 0.2  # Fator de irregularidade
            x += random.uniform(-distortion, distortion)
            y += random.uniform(-distortion, distortion)
            z += random.uniform(-distortion, distortion)
            
            # Vértice distorcido
            vertices.append(x)
            vertices.append(y)
            vertices.append(z)
            
            # Normal aproximada (não é perfeita após a distorção)
            nx = x / (radius + distortion)
            ny = y / (radius + distortion)
            nz = z / (radius + distortion)
            norm = math.sqrt(nx*nx + ny*ny + nz*nz)
            
            normals.append(nx/norm)
            normals.append(ny/norm)
            normals.append(nz/norm)
            
            # Coordenadas de textura
            s = j / slices
            t = i / stacks
            texcoords.append(s)
            texcoords.append(t)
    
    # Gerar índices
    indices = []
    for i in range(stacks):
        for j in range(slices):
            first = i * (slices + 1) + j
            
            # Dois triângulos por face
            indices.append(first)
            indices.append(first + slices + 1)
            indices.append(first + 1)
            
            indices.append(first + slices + 1)
            indices.append(first + slices + 2)
            indices.append(first + 1)
    
    # Converter para arrays numpy
    vertices_array = np.array(vertices, dtype=np.float32)
    normals_array = np.array(normals, dtype=np.float32)
    texcoords_array = np.array(texcoords, dtype=np.float32)
    indices_array = np.array(indices, dtype=np.uint32)
    
    # Criar VAO
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    
    # VBO para vértices
    vbo_vertices = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_vertices)
    glBufferData(GL_ARRAY_BUFFER, vertices_array, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)
    
    # VBO para normais
    vbo_normals = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_normals)
    glBufferData(GL_ARRAY_BUFFER, normals_array, GL_STATIC_DRAW)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(1)
    
    # VBO para texcoords
    vbo_texcoords = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_texcoords)
    glBufferData(GL_ARRAY_BUFFER, texcoords_array, GL_STATIC_DRAW)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(2)
    
    # EBO para índices
    ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices_array, GL_STATIC_DRAW)
    
    # Desligar VAO
    glBindVertexArray(0)
    
    return vao, len(indices_array)
