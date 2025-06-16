"""
Implementações de testes de colisão para o Explorador 3D do Sistema Solar.

Este arquivo contém implementações de diferentes tipos de testes de colisão:
1. Esfera-Esfera
2. Esfera-Ponto
3. AABB-AABB (Caixas alinhadas aos eixos)

FONTE: Alguns algoritmos foram adaptados do livro "Real-Time Collision Detection"
por Christer Ericson, Morgan Kaufmann Publishers, 2005.
"""

import numpy as np
import math

class Sphere:
    def __init__(self, center, radius):
        self.center = np.array(center, dtype=np.float32)
        self.radius = float(radius)

class AABB:
    def __init__(self, min_point, max_point):
        self.min_point = np.array(min_point, dtype=np.float32)
        self.max_point = np.array(max_point, dtype=np.float32)
    
    @staticmethod
    def from_points(points):
        """Cria um AABB a partir de uma lista de pontos"""
        min_point = np.array([float('inf'), float('inf'), float('inf')])
        max_point = np.array([float('-inf'), float('-inf'), float('-inf')])
        
        for point in points:
            min_point = np.minimum(min_point, point)
            max_point = np.maximum(max_point, point)
            
        return AABB(min_point, max_point)
    
    @staticmethod
    def from_sphere(sphere):
        """Cria um AABB que envolve uma esfera"""
        min_point = sphere.center - sphere.radius
        max_point = sphere.center + sphere.radius
        return AABB(min_point, max_point)

class Plane:
    def __init__(self, normal, point):
        self.normal = np.array(normal, dtype=np.float32)
        self.normal = self.normal / np.linalg.norm(self.normal)  # Normalizar
        self.distance = np.dot(self.normal, np.array(point))

def sphere_sphere_collision(sphere1, sphere2):
    """
    Teste de colisão entre duas esferas.
    
    Args:
        sphere1: Objeto Sphere com center e radius
        sphere2: Objeto Sphere com center e radius
        
    Returns:
        bool: True se há colisão, False caso contrário
    """
    # Calcular distância entre os centros
    center_dist_sq = np.sum((sphere1.center - sphere2.center) ** 2)
    
    # Calcular soma dos raios
    sum_radii = sphere1.radius + sphere2.radius
    
    # Há colisão se a distância entre os centros for menor ou igual à soma dos raios
    return center_dist_sq <= (sum_radii * sum_radii)

def sphere_point_collision(sphere, point):
    """
    Teste se um ponto está dentro de uma esfera.
    
    Args:
        sphere: Objeto Sphere com center e radius
        point: Array numpy ou lista [x, y, z] representando o ponto
        
    Returns:
        bool: True se o ponto está dentro da esfera, False caso contrário
    """
    # Converter para array numpy se necessário
    p = np.array(point, dtype=np.float32)
    
    # Calcular distância ao quadrado entre o centro da esfera e o ponto
    dist_sq = np.sum((sphere.center - p) ** 2)
    
    # O ponto está dentro da esfera se a distância for menor ou igual ao raio
    return dist_sq <= (sphere.radius * sphere.radius)

def aabb_aabb_collision(aabb1, aabb2):
    """
    Teste de colisão entre duas caixas alinhadas aos eixos (AABB).
    
    Args:
        aabb1: Objeto AABB com min_point e max_point
        aabb2: Objeto AABB com min_point e max_point
        
    Returns:
        bool: True se há colisão, False caso contrário
    """
    # Verifica se há sobreposição em todos os três eixos
    return (aabb1.min_point[0] <= aabb2.max_point[0] and 
            aabb1.max_point[0] >= aabb2.min_point[0] and
            aabb1.min_point[1] <= aabb2.max_point[1] and 
            aabb1.max_point[1] >= aabb2.min_point[1] and
            aabb1.min_point[2] <= aabb2.max_point[2] and 
            aabb1.max_point[2] >= aabb2.min_point[2])

def plane_sphere_collision(plane, sphere):
    """
    Teste de colisão entre um plano e uma esfera.
    
    Args:
        plane: Objeto Plane com normal e distance
        sphere: Objeto Sphere com center e radius
        
    Returns:
        bool: True se há colisão, False caso contrário
    """
    # Calcular a distância do centro da esfera ao plano
    dist = abs(np.dot(plane.normal, sphere.center) - plane.distance)
    
    # Há colisão se a distância for menor ou igual ao raio
    return dist <= sphere.radius

def create_sphere_for_object(position, radius):
    """Criar uma esfera de colisão para um objeto"""
    return Sphere(position, radius)

def create_aabb_for_object(position, size):
    """Criar uma AABB para um objeto baseado em sua posição e tamanho"""
    half_size = np.array(size) / 2
    min_point = np.array(position) - half_size
    max_point = np.array(position) + half_size
    return AABB(min_point, max_point)
