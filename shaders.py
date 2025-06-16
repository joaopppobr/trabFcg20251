"""
Implementação dos shaders para diferentes modelos de iluminação.

Este arquivo contém:
1. Shader para interpolação Phong (normais interpoladas, iluminação por pixel)
2. Shader para interpolação Gouraud (iluminação por vértice)
"""

from OpenGL.GL import *

# Vertex shader para iluminação Phong (interpolação de normais)
PHONG_VERT_SHADER = """
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec2 texCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 FragPos;
out vec3 Normal;
out vec2 TexCoord;

void main()
{
    // Calcular posição do fragmento no espaço do mundo
    FragPos = vec3(model * vec4(position, 1.0));
    
    // Calcular normal no espaço do mundo
    // Nota: Essa é a maneira correta de transformar normais, mas é computacionalmente cara
    Normal = mat3(transpose(inverse(model))) * normal;
    
    // Passar coordenadas de textura
    TexCoord = texCoord;
    
    // Calcular posição final do vértice
    gl_Position = projection * view * model * vec4(position, 1.0);
}
"""

# Fragment shader para iluminação Phong (cálculo por pixel)
PHONG_FRAG_SHADER = """
#version 330 core
in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;

out vec4 FragColor;

uniform sampler2D textureMap;
uniform vec3 lightPos;
uniform vec3 viewPos;
uniform vec3 lightColor;
uniform vec3 ambientColor;
uniform float shininess;
uniform bool isLightSource;

void main()
{
    // Se for uma fonte de luz, não calcular iluminação
    if (isLightSource) {
        FragColor = texture(textureMap, TexCoord);
        return;
    }
    
    // Amostra a textura
    vec4 texColor = texture(textureMap, TexCoord);
    
    // Normaliza o vetor normal
    vec3 norm = normalize(Normal);
    
    // Vetor direção da luz (do fragmento para a luz)
    vec3 lightDir = normalize(lightPos - FragPos);
    
    // 1. Iluminação ambiente
    vec3 ambient = ambientColor * texColor.rgb;
    
    // 2. Iluminação difusa (modelo de Lambert)
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor * texColor.rgb;
    
    // 3. Iluminação especular (modelo Blinn-Phong)
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 halfwayDir = normalize(lightDir + viewDir);
    float spec = pow(max(dot(norm, halfwayDir), 0.0), shininess);
    vec3 specular = spec * lightColor;
    
    // Combina os componentes
    vec3 result = ambient + diffuse + specular;
    FragColor = vec4(result, texColor.a);
}
"""

# Vertex shader para iluminação Gouraud (cálculo por vértice)
GOURAUD_VERT_SHADER = """
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec2 texCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec3 lightPos;
uniform vec3 viewPos;
uniform vec3 lightColor;
uniform vec3 ambientColor;
uniform float shininess;
uniform bool isLightSource;

out vec2 TexCoord;
out vec3 VertexColor;  // A cor calculada no vértice

void main()
{
    // Posição do vértice no espaço do mundo
    vec3 FragPos = vec3(model * vec4(position, 1.0));
    
    // Transformar a normal
    vec3 Normal = mat3(transpose(inverse(model))) * normal;
    
    // Passar coordenadas de textura
    TexCoord = texCoord;
    
    // Calcular iluminação no vértice (não no fragmento)
    if (isLightSource) {
        VertexColor = vec3(1.0);  // Cor branca para fontes de luz
    }
    else {
        // Normalizar a normal
        vec3 norm = normalize(Normal);
        
        // Vetor direção da luz
        vec3 lightDir = normalize(lightPos - FragPos);
        
        // 1. Iluminação ambiente
        vec3 ambient = ambientColor;
        
        // 2. Iluminação difusa (Lambert)
        float diff = max(dot(norm, lightDir), 0.0);
        vec3 diffuse = diff * lightColor;
        
        // 3. Iluminação especular (Blinn-Phong)
        vec3 viewDir = normalize(viewPos - FragPos);
        vec3 halfwayDir = normalize(lightDir + viewDir);
        float spec = pow(max(dot(norm, halfwayDir), 0.0), shininess);
        vec3 specular = spec * lightColor;
        
        // Combinar componentes (a textura será aplicada no fragment shader)
        VertexColor = ambient + diffuse + specular;
    }
    
    // Calcular posição final do vértice
    gl_Position = projection * view * model * vec4(position, 1.0);
}
"""

# Fragment shader para iluminação Gouraud
GOURAUD_FRAG_SHADER = """
#version 330 core
in vec2 TexCoord;
in vec3 VertexColor;  // Cor calculada no vertex shader

out vec4 FragColor;

uniform sampler2D textureMap;
uniform bool isLightSource;

void main()
{
    // Amostra a textura
    vec4 texColor = texture(textureMap, TexCoord);
    
    if (isLightSource) {
        FragColor = texColor;
    }
    else {
        // Aplica a cor calculada no vértice à textura
        FragColor = vec4(VertexColor * texColor.rgb, texColor.a);
    }
}
"""

def compile_shader(source, shader_type):
    """Compila um shader a partir de seu código fonte."""
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    
    # Verificar erros de compilação
    success = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not success:
        info_log = glGetShaderInfoLog(shader).decode('utf-8')
        print(f"ERRO DE COMPILAÇÃO DE SHADER ({shader_type}):")
        print(info_log)
        glDeleteShader(shader)
        return None
        
    return shader

def create_shader_program(vertex_source, fragment_source):
    """Cria um programa de shader compilando e linkando os shaders vertex e fragment."""
    # Compilar shaders
    vertex_shader = compile_shader(vertex_source, GL_VERTEX_SHADER)
    if not vertex_shader:
        return None
        
    fragment_shader = compile_shader(fragment_source, GL_FRAGMENT_SHADER)
    if not fragment_shader:
        glDeleteShader(vertex_shader)
        return None
    
    # Criar e linkar programa
    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    
    # Verificar erros de linkagem
    success = glGetProgramiv(program, GL_LINK_STATUS)
    if not success:
        info_log = glGetProgramInfoLog(program).decode('utf-8')
        print(f"ERRO DE LINKAGEM DE PROGRAMA:")
        print(info_log)
        glDeleteProgram(program)
        return None
    
    # Limpar shaders
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)
    
    return program

def init_shaders():
    """Inicializa todos os shaders necessários."""
    # Criar programa para iluminação Phong
    phong_program = create_shader_program(PHONG_VERT_SHADER, PHONG_FRAG_SHADER)
    if not phong_program:
        print("Falha ao criar programa de shader Phong!")
        return None
        
    # Criar programa para iluminação Gouraud
    gouraud_program = create_shader_program(GOURAUD_VERT_SHADER, GOURAUD_FRAG_SHADER)
    if not gouraud_program:
        print("Falha ao criar programa de shader Gouraud!")
        glDeleteProgram(phong_program)
        return None
    
    print("Shaders inicializados com sucesso")
    
    return {
        'phong': phong_program,
        'gouraud': gouraud_program
    }
