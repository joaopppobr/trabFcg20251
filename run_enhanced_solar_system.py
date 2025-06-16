"""
Explorador 3D do Sistema Solar - Versão Avançada

Este programa implementa uma visualização interativa do Sistema Solar utilizando:
- Modelos 3D complexos
- Shaders personalizados (Phong e Gouraud)
- Detecção de colisões
- Curvas de Bézier para órbitas
- Animação baseada em tempo

"""
import os
import pygame
from pygame.locals import *
from OpenGL.GL import *
import sys

# Importar o SolarExplorer do arquivo principal
from solar_explorer import SolarExplorer

def main():
    # Verificar se os diretórios necessários existem
    if not os.path.exists("models"):
        os.makedirs("models")
    
    if not os.path.exists("textures"):
        os.makedirs("textures")
        print("Pasta 'textures' criada. Por favor, adicione texturas para os planetas.")
    
    # Iniciar o explorador solar avançado
    print("Iniciando Explorador 3D do Sistema Solar - Versão Avançada")
    print("\nControles:")
    print("  Mouse: Rotacionar câmera")
    print("  Roda do mouse: Zoom")
    print("  C: Alternar entre câmera orbital e livre")
    print("  WASD: Mover câmera livre")
    print("  SPACE/SHIFT: Subir/descer com câmera livre")
    print("  O: Mostrar/ocultar órbitas")
    print("  P: Pausar/continuar simulação")
    print("  +/-: Aumentar/diminuir velocidade da simulação")
    print("  ESC: Sair")
    
    # Criar e executar o explorador
    explorer = SolarExplorer()
    explorer.run()

if __name__ == "__main__":
    main()
