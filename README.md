# Explorador 3D do Sistema Solar

Este projeto implementa uma aplicação gráfica interativa para visualização e exploração do Sistema Solar em 3D, desenvolvida como trabalho final da disciplina de Fundamentos de Computação Gráfica.

## Autores
- [Seu Nome]
- [Nome do Parceiro]

## Características Principais

- Visualização 3D de planetas com texturas realistas
- Órbitas planetárias calculadas usando curvas de Bézier
- Animação baseada em tempo
- Dois modos de câmera: orbital e livre
- Sistema de detecção de colisão entre asteroides e planetas
- Iluminação realista usando shaders personalizados
  - Modelo de iluminação Phong (por pixel)
  - Modelo de iluminação Gouraud (por vértice)
- Modelos 3D complexos (incluindo a vaca exigida no trabalho)
- Mapeamento de texturas em todos os objetos

## Requisitos Implementados

1. **Objetos com malhas poligonais complexas**
   - Modelo complexo de vaca (cow.obj)
   - Planetas representados com esferas subdivididas

2. **Transformações geométricas**
   - Rotação dos planetas em torno de seus eixos
   - Translação dos planetas em suas órbitas
   - Transformações hierárquicas (Lua orbitando a Terra)
   - Implementação manual de matrizes de transformação (sem usar funções prontas como glm::rotate)

3. **Câmeras virtuais**
   - Câmera orbital: gira em torno do sistema solar
   - Câmera livre: permite navegação em todas as direções
   - Implementação manual de matrizes de visualização (sem usar gluLookAt)

4. **Múltiplas instâncias de objetos**
   - Asteroides gerados a partir do mesmo modelo base
   - Reutilização de geometria com diferentes transformações

5. **Testes de intersecção**
   - Esfera-Esfera (colisões de asteroides com planetas)
   - Esfera-Ponto (detecção de pontos dentro de esferas)
   - AABB-AABB (caixas delimitadoras)

6. **Modelos de iluminação**
   - Iluminação difusa (Lambert)
   - Iluminação especular (Blinn-Phong)
   - Distintos modelos de sombreamento:
     - Phong shading (interpolação de normais, iluminação por pixel)
     - Gouraud shading (iluminação por vértice)

7. **Mapeamento de texturas**
   - Texturização de todos os objetos
   - Texturas procedurais como fallback

8. **Curvas de Bézier**
   - Órbitas planetárias construídas usando curvas de Bézier cúbicas
   - Movimento dos planetas ao longo das curvas

9. **Animação baseada em tempo**
   - Todas as animações são calculadas com base no delta-time
   - Velocidade da simulação ajustável

## Como Executar

1. Certifique-se de ter Python 3.6 ou superior instalado
2. Instale as dependências:
   ```
   pip install pygame PyOpenGL numpy
   ```
3. Coloque o arquivo "cow.obj" na pasta "models/" (baixe de sources disponíveis)
4. Coloque as texturas dos planetas na pasta "textures/" 
5. Execute o programa:
   ```
   python run_enhanced_solar_system.py
   ```

## Estrutura do Projeto

- **solar_explorer.py**: Arquivo principal do sistema
- **shaders.py**: Implementação dos shaders GLSL para iluminação
- **collisions.py**: Sistema de detecção de colisões
- **model_loader.py**: Carregador de modelos OBJ
- **run_enhanced_solar_system.py**: Script para executar o sistema
- **models/**: Diretório para modelos 3D
- **textures/**: Diretório para texturas dos planetas

## Controles

- **Mouse**: Rotação da câmera
- **Roda do mouse**: Zoom
- **C**: Alternar entre câmera orbital e livre
- **WASD**: Mover câmera livre
- **ESPAÇO/SHIFT**: Mover câmera para cima/baixo
- **O**: Mostrar/ocultar órbitas
- **P**: Pausar/continuar simulação
- **+/-**: Aumentar/diminuir velocidade da simulação
- **ESC**: Sair

## Uso de ferramentas de IA

Para o desenvolvimento deste projeto, utilizamos o GitHub Copilot como ferramenta de assistência à programação. A ferramenta foi particularmente útil para:

- Gerar estruturas básicas de código e esqueletos de classes
- Auxiliar na implementação das matrizes de transformação e visualização
- Implementação dos shaders GLSL
- Criação das funções de teste de colisão

No entanto, a compreensão profunda dos conceitos de Computação Gráfica e a capacidade de estruturar o projeto como um todo continuaram sendo essenciais e de responsabilidade nossa como desenvolvedores.
