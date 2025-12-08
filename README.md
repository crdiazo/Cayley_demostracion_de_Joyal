# Proyecto MD - Demostración de Joyal para la Fórmula de Cayley  

Este proyecto implementa una **visualización interactiva local** de la biyección de Joyal, un enfoque combinatorio elegante que explica por qué el número de árboles etiquetados con $n$ vértices es:

$$
n^{\,n-2}
$$

A través de una interfaz gráfica hecha en **pygame**, el programa permite construir funciones, visualizar sus grafos dirigidos, extraer la permutación asociada tanto en **notación funcional** como en **notación cíclica**, y generar una matriz clave para un cifrado Hill dependiente de dicha función.

La implementación es completamente local, optimizada para usarse desde escritorio y para integrarse en repositorios de GitHub.

---

## Características Principales

### 1. Elección dinámica del tamaño $n$
Al iniciar la aplicación, el usuario puede elegir cualquier $n \ge 2$.  
A partir de este valor, el sistema:

- genera la estructura base,
- crea la disposición circular de vértices,
- prepara las estructuras para el cifrado Hill de tamaño $n \times n$.

---

### 2. Ingreso interactivo de la función $f : \{1,2,\dots,n\} \to \{1,2,\dots,n\}$
El usuario ingresa su función como una lista separada por comas:

$1,2,4,6,6,6,7,8,9$

El programa valida automáticamente:

- Longitud correcta  
- Valores en rango  
- Dominio consistente  

---

### 3. Visualización del grafo dirigido (pygame)
Tras ingresar la función, la aplicación dibuja:

- Un nodo por cada vértice  
- Una flecha desde $i$ hacia $f(i)$  
- Distribución circular uniforme  
- Actualización visual en tiempo real  

Ideal para explicar la construcción del árbol codificado en la demostración de Joyal.

---

### 4. Permutaciones en **notación funcional** y **cíclica**
Una vez ingresada la función, el programa imprime:

#### Notación funcional:
Ejemplo para $n = 9$:

$(2, 4, 5, 6, 6, 6, 7, 8, 9)$

#### Notación cíclica
Ejemplo:

$(1 2 4 6)(3 5)(7)(8)(9)$

La notación cíclica permite visualizar inmediatamente los ciclos dirigidos, pieza clave dentro de la biyección de Joyal.

---

### 5. Cifrado Hill generalizado a tamaño $n \times n$
A partir de la función ingresada, el sistema genera una matriz clave:

- Cuadrada $n \times n$ 
- Módulo 30  
- Alfabeto extendido: A–Z, Ñ, coma, punto y espacio  

El usuario puede:

- **Encriptar** mensajes  
- **Desencriptar** mensajes  
- Ver posibles errores cuando la matriz no es invertible  
- Recibir automáticamente una matriz alternativa válida cuando se requiera  

---

## Ejemplos de Uso

### Ejemplo 1: Construcción completa desde una función  
Supongamos que el usuario elige:

**n = 9**

Y luego ingresa la función:

$1,2,4,6,6,6,7,8,9$

El sistema mostrará:

#### Notación funcional:

$(2, 4, 5, 6, 6, 6, 7, 8, 9)$

#### Notación cíclica:

$(1 2 4 6)(3 5)(7)(8)(9)$

#### Interpretación:
- Hay un ciclo grande: **1 → 2 → 4 → 6 → 6**  
- Un ciclo pequeño: **3 → 5 → 6**  
- Vértices fijos: 7, 8, 9  
- El grafo se dibuja automáticamente en pygame, con flechas indicando cada transición.

---

### Ejemplo 2: Detección visual de ciclos  
Si el usuario ingresa:

$2,3,1,5,4$

Con **n = 5**, el resultado será:

#### Notación funcional:

$(2, 3, 1, 5, 4)$

#### Notación cíclica:

$(1 2 3)(4 5)$

El grafo mostraría:

- Un ciclo de longitud 3 → **1 → 2 → 3 → 1**  
- Un ciclo de longitud 2 → **4 ↔ 5**  

Ambos ciclos se representan gráficamente en la ventana mediante flechas cerradas.

---

### Ejemplo 3: Cifrado Hill paso a paso  
Supongamos que la matriz generada desde $f$ (para $n = 3$) es:

$$
K =
\begin{pmatrix}
2 & 1 & 3 \\
0 & 1 & 4 \\
5 & 2 & 1
\end{pmatrix}
\quad (\text{mod } 30)
$$

Y el usuario ingresa el mensaje:

HOLA MUNDO

El programa:

1. Convierte cada letra a su valor numérico (A=0, …, espacio=29).  
2. Rellena con caracteres de control para ajustar múltiplos de 3.  
3. Encripta usando $C = K \cdot P \pmod{30}$
4. Devuelve el texto cifrado en pantalla.  
5. Permite aplicar la inversa de $K$ para recuperar el mensaje.

Esto demuestra que la estructura combinatoria de la función puede alimentar un sistema criptográfico concreto.

---

## Propósito Académico

Este repositorio funciona como una herramienta pedagógica para comprender:

- La demostración de Joyal para la fórmula de Cayley  
- La naturaleza combinatoria de las funciones y sus ciclos  
- La relación entre funciones y árboles en $\mathcal{T}_n$ 
- Cómo los ciclos funcionales pueden inducir matrices útiles en criptografía  
- La interacción entre teoría, visualización y programación  

El objetivo es unir combinatoria, teoría de grafos, permutaciones y criptografía en un solo proyecto integral.

---

## Tecnologías Utilizadas

- **Python 3**
- **Pygame** – Visualización de grafos  
- **NumPy** – Operaciones matriciales  
- **Tkinter** – Entrada de datos  
- **Algoritmos incluidos:**
  - Búsqueda y descomposición en ciclos  
  - Notación funcional y cíclica  
  - Generación de grafos dirigidos  
  - Determinante de Bareiss  
  - Inversa modular  
  - Hill Cipher generalizado  

---

## Autores

- **Martin Lora Caro**  
- **Cristian Andrés Díaz Ortega**  
- **Jhon Edison Prieto Artunduaga**

Proyecto desarrollado para el curso de **Matemáticas Discretas I** de la Universidad Nacional de Colombia.
