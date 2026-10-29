
import streamlit as st
import math
import ast
import operator

# ==========================================
# CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="Calculadora Científica",
    page_icon="🧮",
    layout="centered"
)

# ==========================================
# DISEÑO VISUAL
# ==========================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #312e81);
}

h1 {
    text-align: center;
    color: #67e8f9;
}

.subtitulo {
    text-align: center;
    color: #cbd5e1;
    margin-bottom: 25px;
}

.pantalla {
    background: #030712;
    border: 2px solid #0891b2;
    border-radius: 15px;
    padding: 20px;
    text-align: right;
    color: #67e8f9;
    font-size: 30px;
    font-weight: bold;
    overflow-wrap: anywhere;
}

div.stButton > button {
    width: 100%;
    height: 50px;
    border-radius: 10px;
    font-size: 18px;
    font-weight: bold;
    background-color: #263449;
    color: white;
    border: 1px solid #475569;
}

div.stButton > button:hover {
    background-color: #2563eb;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# VARIABLES DE SESIÓN
# ==========================================

if "expresion" not in st.session_state:
    st.session_state.expresion = ""

if "resultado" not in st.session_state:
    st.session_state.resultado = "0"

if "grados" not in st.session_state:
    st.session_state.grados = True

if "historial" not in st.session_state:
    st.session_state.historial = []

# ==========================================
# MOTOR DE CÁLCULO
# ==========================================

def factorial(n):
    if n < 0 or n > 170 or n != int(n):
        raise ValueError("Factorial inválido")
    return math.factorial(int(n))


def evaluar(nodo):

    operaciones = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod
    }

    unarios = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg
    }

    if isinstance(nodo, ast.Expression):
        return evaluar(nodo.body)

    if isinstance(nodo, ast.Constant):
        if type(nodo.value) not in (int, float):
            raise ValueError("Valor inválido")
        return nodo.value

    if isinstance(nodo, ast.BinOp) and type(nodo.op) in operaciones:
        a = evaluar(nodo.left)
        b = evaluar(nodo.right)

        if isinstance(nodo.op, ast.Pow) and abs(b) > 1000:
            raise ValueError("Exponente demasiado grande")

        resultado = operaciones[type(nodo.op)](a, b)

        if isinstance(resultado, complex) or not math.isfinite(resultado):
            raise ValueError("Resultado inválido")

        return resultado

    if isinstance(nodo, ast.UnaryOp) and type(nodo.op) in unarios:
        return unarios[type(nodo.op)](evaluar(nodo.operand))

    if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name):

        funciones = {
            "sin": lambda x: math.sin(
                math.radians(x) if st.session_state.grados else x
            ),
            "cos": lambda x: math.cos(
                math.radians(x) if st.session_state.grados else x
            ),
            "tan": lambda x: math.tan(
                math.radians(x) if st.session_state.grados else x
            ),
            "sqrt": math.sqrt,
            "log": math.log10,
            "ln": math.log,
            "fact": factorial,
            "asin": lambda x: math.degrees(math.asin(x)) if st.session_state.grados else math.asin(x),
            "acos": lambda x: math.degrees(math.acos(x)) if st.session_state.grados else math.acos(x),
            "atan": lambda x: math.degrees(math.atan(x)) if st.session_state.grados else math.atan(x)
        }

        nombre = nodo.func.id

        if nombre not in funciones or len(nodo.args) != 1:
            raise ValueError("Función no permitida")

        return funciones[nombre](evaluar(nodo.args[0]))

    if isinstance(nodo, ast.Name):
        constantes = {
            "pi": math.pi,
            "e": math.e
        }

        if nodo.id in constantes:
            return constantes[nodo.id]

    raise ValueError("Expresión no válida")


def calcular(expresion):

    texto = expresion.replace("×", "*")
    texto = texto.replace("÷", "/")
    texto = texto.replace("^", "**")
    texto = texto.replace("π", "pi")
    texto = texto.replace("²", "**2")
    texto = texto.replace("%", "/100")

    arbol = ast.parse(texto, mode="eval")
    resultado = evaluar(arbol)

    if isinstance(resultado, complex) or not math.isfinite(resultado):
        raise ValueError("Resultado inválido")

    return resultado


# ==========================================
# FUNCIONES DE LOS BOTONES
# ==========================================

def pulsar(valor):

    if valor == "AC":
        st.session_state.expresion = ""
        st.session_state.resultado = "0"

    elif valor == "⌫":
        st.session_state.expresion = st.session_state.expresion[:-1]

    elif valor == "=":

        if st.session_state.expresion:
            try:
                texto = st.session_state.expresion

                abiertos = texto.count("(") - texto.count(")")
                texto += ")" * max(0, abiertos)

                resultado = calcular(texto)

                anterior = st.session_state.expresion

                st.session_state.resultado = f"{resultado:.10g}"
                st.session_state.historial.insert(
                    0,
                    f"{anterior} = {resultado:.10g}"
                )

                st.session_state.historial = st.session_state.historial[:10]
                st.session_state.expresion = st.session_state.resultado

            except (
                ValueError,
                TypeError,
                SyntaxError,
                ZeroDivisionError,
                OverflowError
            ):
                st.session_state.resultado = "Error"

    elif valor == "DEG/RAD":
        st.session_state.grados = not st.session_state.grados

    else:

        funciones = [
            "sin", "cos", "tan",
            "log", "ln", "sqrt",
            "fact", "asin", "acos", "atan"
        ]

        if valor in funciones:
            st.session_state.expresion += valor + "("

        elif valor == "√":
            st.session_state.expresion += "sqrt("

        elif valor == "x²":
            st.session_state.expresion += "**2"

        elif valor == "n!":
            st.session_state.expresion += "fact("

        else:
            st.session_state.expresion += valor


# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================

st.title("🧮 CALCULADORA CIENTÍFICA")

st.markdown(
    '<div class="subtitulo">Sistema de operaciones matemáticas avanzadas</div>',
    unsafe_allow_html=True
)

# Modo angular

col1, col2 = st.columns([1, 2])

with col1:
    etiqueta = "DEG" if st.session_state.grados else "RAD"

    if st.button(etiqueta, use_container_width=True):
        pulsar("DEG/RAD")
        st.rerun()

with col2:
    st.info(
        "Trabajando en grados" if st.session_state.grados
        else "Trabajando en radianes"
    )

# Pantalla

st.markdown("### Pantalla")

st.code(
    st.session_state.expresion or "0",
    language=None
)

st.markdown(
    f'<div class="pantalla">{st.session_state.resultado}</div>',
    unsafe_allow_html=True
)

st.write("")

# ==========================================
# BOTONES
# ==========================================

botones = [
    ["sin", "cos", "tan", "AC"],
    ["asin", "acos", "atan", "⌫"],
    ["(", ")", "√", "^"],
    ["log", "ln", "x²", "÷"],
    ["7", "8", "9", "×"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["π", "e", "n!", "="],
    ["0", ".", "%", "AC"]
]

for i, fila in enumerate(botones):

    columnas = st.columns(4)

    for j, valor in enumerate(fila):

        with columnas[j]:

            if st.button(
                valor,
                key=f"boton_{i}_{j}",
                use_container_width=True
            ):

                pulsar(valor)
                st.rerun()

# ==========================================
# HISTORIAL
# ==========================================

st.divider()

with st.expander("📚 Historial de operaciones"):

    if st.session_state.historial:

        for operacion in st.session_state.historial:
            st.write("•", operacion)

    else:
        st.caption("Todavía no hay operaciones.")

    if st.button("Borrar historial"):
        st.session_state.historial = []
        st.rerun()

st.caption("Desarrollado con Python y Streamlit")



