import OpenGL.GL as gl
import numpy as np

def compile_shader(source, shader_type):
    shader = gl.glCreateShader(shader_type)
    gl.glShaderSource(shader, source)
    gl.glCompileShader(shader)
    if not gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS):
        raise RuntimeError(gl.glGetShaderInfoLog(shader).decode())
    return shader

def create_program(vertex_src, fragment_src):
    program = gl.glCreateProgram()
    vs = compile_shader(vertex_src, gl.GL_VERTEX_SHADER)
    fs = compile_shader(fragment_src, gl.GL_FRAGMENT_SHADER)
    gl.glAttachShader(program, vs)
    gl.glAttachShader(program, fs)
    gl.glLinkProgram(program)
    if not gl.glGetProgramiv(program, gl.GL_LINK_STATUS):
        raise RuntimeError(gl.glGetProgramInfoLog(program).decode())
    gl.glDeleteShader(vs)
    gl.glDeleteShader(fs)
    return program

# Lambert (difusa) + Blinn-Phong (specular) + textura
VERTEX_SHADER_GOURAUD = """
#version 120
attribute vec3 position;
attribute vec3 normal;
attribute vec2 texcoord;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec3 lightPos;
uniform vec3 viewPos;
varying vec3 color;
varying vec2 v_texcoord;

void main() {
    vec3 N = normalize(mat3(model) * normal);
    vec3 L = normalize(lightPos - vec3(model * vec4(position, 1.0)));
    vec3 V = normalize(viewPos - vec3(model * vec4(position, 1.0)));
    vec3 H = normalize(L + V);

    float diff = max(dot(N, L), 0.0);
    float spec = pow(max(dot(N, H), 0.0), 32.0);

    vec3 diffuse = diff * vec3(1.0, 1.0, 1.0);
    vec3 specular = spec * vec3(1.0);
    vec3 ambient = 0.15 * vec3(1.0, 1.0, 1.0);

    color = ambient + diffuse + specular;
    v_texcoord = texcoord;
    gl_Position = projection * view * model * vec4(position, 1.0);
}
"""

FRAGMENT_SHADER_GOURAUD = """
#version 120
uniform sampler2D tex;
varying vec3 color;
varying vec2 v_texcoord;
void main() {
    vec4 texColor = texture2D(tex, v_texcoord);
    gl_FragColor = vec4(color, 1.0) * texColor;
}
"""

VERTEX_SHADER_PHONG = """
#version 120
attribute vec3 position;
attribute vec3 normal;
attribute vec2 texcoord;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
varying vec3 fragPos;
varying vec3 fragNormal;
varying vec2 v_texcoord;
void main() {
    fragPos = vec3(model * vec4(position, 1.0));
    fragNormal = normalize(mat3(model) * normal);
    v_texcoord = texcoord;
    gl_Position = projection * view * model * vec4(position, 1.0);
}
"""

FRAGMENT_SHADER_PHONG = """
#version 120
uniform vec3 lightPos;
uniform vec3 viewPos;
uniform sampler2D tex;
varying vec3 fragPos;
varying vec3 fragNormal;
varying vec2 v_texcoord;
void main() {
    vec3 N = normalize(fragNormal);
    vec3 L = normalize(lightPos - fragPos);
    vec3 V = normalize(viewPos - fragPos);
    vec3 H = normalize(L + V);

    float diff = max(dot(N, L), 0.0);
    float spec = pow(max(dot(N, H), 0.0), 32.0);

    vec3 diffuse = diff * vec3(1.0, 1.0, 1.0);
    vec3 specular = spec * vec3(1.0);
    vec3 ambient = 0.15 * vec3(1.0, 1.0, 1.0);

    vec3 color = ambient + diffuse + specular;
    vec4 texColor = texture2D(tex, v_texcoord);
    gl_FragColor = vec4(color, 1.0) * texColor;
}
"""

def get_gouraud_program():
    return create_program(VERTEX_SHADER_GOURAUD, FRAGMENT_SHADER_GOURAUD)

def get_phong_program():
    return create_program(VERTEX_SHADER_PHONG, FRAGMENT_SHADER_PHONG)

# Exemplo de uso (no seu SolarExplorer, para desenhar uma esfera Gouraud e uma Phong):
# from shading_models import get_gouraud_program, get_phong_program
# gouraud_prog = get_gouraud_program()
# phong_prog = get_phong_program()
# ... depois, para desenhar:
# gl.glUseProgram(gouraud_prog)
# ...set uniforms, bind VBO/VAO, draw sphere...
# gl.glUseProgram(0)
# gl.glUseProgram(phong_prog)
# ...set uniforms, bind VBO/VAO, draw sphere...
# gl.glUseProgram(0)
