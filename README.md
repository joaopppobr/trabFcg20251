# Explorador 3D do Sistema Solar

Este projeto é uma aplicação interativa desenvolvida em Python para visualização e exploração do Sistema Solar em 3D, com foco em conceitos fundamentais de Computação Gráfica. O sistema foi projetado para demonstrar, de forma didática e visual, a aplicação de matrizes de transformação, iluminação via shaders, detecção de colisões, animação baseada em tempo, curvas de Bézier e manipulação de modelos 3D complexos.

## Descrição Geral

A aplicação simula o Sistema Solar com planetas, luas, um asteroide animado e um satélite artificial (modelo complexo). O usuário pode alternar entre diferentes modos de câmera, visualizar órbitas, pausar a simulação, ajustar a velocidade e observar colisões em tempo real. Todos os objetos são texturizados e iluminados com modelos realistas.

## Estrutura e Funcionamento do Código

### 1. Arquitetura dos Arquivos

- **solar_explorer.py**  
  Arquivo principal. Contém a classe `SolarExplorer`, responsável por toda a lógica da simulação, renderização, controle de câmera, animação, carregamento de texturas e modelos, e interação com o usuário.

- **shading_models.py**  
  Implementa shaders GLSL para iluminação Gouraud (por vértice) e Phong (por pixel), além de funções utilitárias para compilação e linkagem dos programas de shader.

- **collisions.py**  
  Implementa testes de colisão entre esferas, pontos e caixas AABB, usados para detectar interações físicas entre asteroides, planetas e limites da cena.

- **run_enhanced_solar_system.py**  
  Script de inicialização da aplicação. Exibe instruções de uso e executa o loop principal.

- **models/**  
  Contém modelos 3D no formato OBJ, incluindo o satélite (ex: Hubble) e outros objetos complexos.

- **textures/**  
  Contém imagens de textura para todos os planetas, satélite, asteroide e fundo estelar.

---

### 2. Principais Funcionalidades

#### a) Modelagem e Transformações

- **Matrizes Manuais:**  
  Todas as matrizes de modelagem, visualização (view) e projeção são implementadas manualmente usando NumPy, sem uso de funções utilitárias como `gluLookAt` ou `gluPerspective`.
- **Transformações Hierárquicas:**  
  Lua orbitando a Terra, satélite orbitando a Terra, planetas orbitando o Sol.
- **Curvas de Bézier:**  
  O asteroide se move ao longo de uma curva de Bézier cúbica, com pontos de controle definidos dinamicamente.

#### b) Iluminação e Shaders

- **Shader Gouraud:**  
  Utilizado para planetas e luas, calcula iluminação por vértice (Lambert + Blinn-Phong).
- **Shader Phong:**  
  Utilizado para o Sol e para Vênus, calcula iluminação por pixel, demonstrando interpolação de normais e iluminação mais realista.
- **Configuração de Luz:**  
  A fonte de luz principal está na posição do Sol. O modelo de iluminação é atualizado a cada frame.

#### c) Texturização

- **Mapeamento de Texturas:**  
  Todos os objetos possuem texturas realistas. Caso a textura não seja encontrada, uma textura procedural é gerada como fallback.
- **Texturas Diferenciadas:**  
  Cada planeta, lua, asteroide e satélite possui sua própria textura.

#### d) Modelos 3D Complexos

- **Satélite Artificial:**  
  Um modelo OBJ complexo (ex: Hubble) é carregado e animado em órbita da Terra.
- **Malhas Procedurais:**  
  Esferas para planetas e luas são geradas por subdivisão de triângulos.

#### e) Animação Baseada em Tempo

- **Delta Time:**  
  Todas as animações (translação, rotação, órbitas, movimento do asteroide) são baseadas no tempo real decorrido, garantindo suavidade independente do desempenho da máquina.
- **Velocidade Ajustável:**  
  O usuário pode aumentar ou diminuir a velocidade da simulação.

#### f) Câmeras Virtuais

- **Câmera Orbital:**  
  Permite girar ao redor do sistema solar com o mouse.
- **Câmera Livre:**  
  Permite navegação em primeira pessoa com WASD e mouse.
- **Alternância Dinâmica:**  
  O usuário pode alternar entre os modos de câmera a qualquer momento.

#### g) Detecção de Colisões

- **Esfera-Esfera:**  
  Detecta colisão entre asteroide e planetas.
- **Esfera-Ponto:**  
  Detecta se um ponto está dentro de uma esfera (usado em algumas interações).
- **AABB-AABB:**  
  Garante que o asteroide não saia dos limites da cena.

#### h) Interação com o Usuário

- **Teclado e Mouse:**  
  - Mouse: Rotação da câmera orbital
  - Roda do mouse: Zoom
  - C: Alterna entre câmera orbital e livre
  - WASD: Move a câmera livre
  - Espaço/Shift: Sobe/desce a câmera livre
  - O: Mostra/oculta órbitas
  - P: Pausa/continua a simulação
  - +/-: Ajusta velocidade da simulação
  - N: Cria um novo asteroide
  - ESC: Sai do programa

- **Mensagens de Colisão:**  
  Quando o asteroide colide com um planeta, uma mensagem de aviso é exibida na tela.

---

## Como Executar

1. **Pré-requisitos:**  
   - Python 3.6+
   - Instale as dependências:
     ```
     pip install pygame PyOpenGL numpy pywavefront
     ```
2. **Modelos e Texturas:**  
   - Coloque os arquivos OBJ dos modelos em `models/`
   - Coloque as texturas em `textures/`
3. **Execução:**  
   ```
   python run_enhanced_solar_system.py
   ```

---

## Observações Técnicas

- **Matrizes de Transformação:**  
  Todas as transformações geométricas, de câmera e projeção são feitas manualmente, conforme exigido em trabalhos de Computação Gráfica.
- **Shaders:**  
  Os shaders são escritos em GLSL e compilados em tempo de execução.
- **Organização Modular:**  
  O código é modularizado para facilitar manutenção, testes e extensão.
- **Fallbacks:**  
  Caso algum recurso (modelo ou textura) não seja encontrado, o sistema gera alternativas procedurais para garantir funcionamento.

---

## Créditos

- Modelos 3D do satélite Hubble: [Sketchfab](https://sketchfab.com/3d-models/satellite-d232fe608c874009bad9613c8093a972#download)
- Texturas planetárias: Diversas fontes públicas
- Desenvolvimento: João Pedro Porto Pires de Oliveira
- Assistência de IA: GitHub Copilot (auxílio em estruturas e sugestões de código)

---

## Licença

Este projeto é acadêmico e não possui fins comerciais.  
Para uso de modelos e texturas, verifique as licenças dos respectivos autores.
