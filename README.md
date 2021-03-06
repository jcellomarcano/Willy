### Willy*

- [Willy*](#willy-)
- [¿Qué es?](#qué-es)
- [¿Cómo correrlo?](#cómo-correrlo)
- [Versiones](#versiones)
  * [Versión Final 3.0](#versión-final-30)
    + [Otras cosas importantes que resaltar:](#otras-cosas-importantes-que-resaltar)
    + [Consideraciones en cuanto a la impresión:](#consideraciones-en-cuanto-a-la-impresión)
    + [Consideraciones en cuanto a la implementación:](#consideraciones-en-cuanto-a-la-implementación)
    + [Versiones anteriores](#versiones-anteriores)
- [Sobre la implementación](#sobre-la-implementación)
  * [Sobre el Lexer](#sobre-el-lexer)
  * [Sobre el Parser](#sobre-el-parser)
  * [Sobre el Interpretador](#sobre-el-interpretador)
    + [Interpretar los mundos](#interpretar-los-mundos)
    + [Interpretar las tareas](#interpretar-las-tareas)
  * [Sobre el Simulador](#sobre-el-simulador)
- [Archivos de Prueba](#archivos-de-prueba)
    + [PickStars.txt](#pickstarstxt)
    + [WillyCleanItsRoom.txt](#willycleanitsroomtxt)
    + [EatClean.txt](#eatcleantxt)
    + [WriteFirstLetterOfMyName.txt](#writefirstletterofmynametxt)
    + [ComesHappyToUni.txt](#comeshappytounitxt)
    + [WillyScan.txt](#willyscantxt)
    + [EsferasDelDragon.txt](#esferasdeldragontxt)
    + [Laberinto.txt](#laberintotxt)
    + [TicTacToe.txt](#tictactoetxt)
    + [Otros](#otros)
- [Conclusión](#conclusión)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>




# ¿Qué es?

**Este es un interpretador del lenguaje Willy***, que determina un ambiente de programación para un robot.

:robot: Este puede interactuar con objetos en un mundo y desplazarse por el mismo a través de cuadrículas de tamaño finito.

Para más detalles del lenguaje Willy > [willy.pdf](https://github.com/MaferMazu/Willy/blob/Parser/willy.pdf)

Este interpretador se hizo como proyecto para la materia de Traductores de la Universidad Simón Bolívar, el trimestre Ene-Mar de 2020

Y fue desarrollado por: 

- [@jcellomarcano](https://github.com/jcellomarcano)

- [@mafermazu](https://github.com/MaferMazu)

# ¿Cómo correrlo? 

1. Tener descargado ply > [ply](https://www.dabeaz.com/ply/)

2. Descargar el repositorio

3. Entrar en la terminal del sistema en la dirección del repositorio y realizar en la línea de comandos:

  `$ ./makefile.sh` 

  (Nota: se espera que no existan otros ejecutables con el mismo nombre, es decir, que no se tenga en el $PATH otro comando que se llame willy)


  Si se tiene otros ejecutables en el PATH se pueden eliminar utilizando:

  `$ export PATH=${PATH%:DireccionDeComandoAEliminarDelPath}` 
  
  (Al ejecutar el makefile se copian los archivos .py en ~/.local/bin para poder ejecutar a willy)

4. Luego se puede ejecutar el programa Willy, usando:

  1) `$ willy <direcciondearchivoenlenguajewilly*> <-a|--automatico> <#DeSegundos>` 
  
  2) `$ willy <direcciondearchivoenlenguajewilly*> <-m|--manual>`

  

Todo lo que esté entre <> es opcional y '|' significa que es uno u otro.

 - En el modo automático se debe asignar un número en float con los segundos en que se ejecutará el programa paso a paso.
 

 - En el modo manual, cada paso se va a ejecutar al pisar la tecla enter.


La forma de detener la ejecución de ambos modos es usar ctrl + c

La forma de correr el programa y que se ejecute todo es colocarlo en modo automático y no colocando segundos.

**Dentro del directorio Pruebas se encuentran algunos archivos en lenguaje Willy**. Se puede conocer un poco más de esto aquí > [Archivos de Prueba](#archivos-de-prueba)

Para entender mejor cómo corre el programa leer sobre la [Versión Final 3.0](#versión-final-30) y [Sobre la implementación](#sobre-la-implementación)


# Versiones

## Versión Final 3.0
12/04/2020 

El interpretador realiza correctamente la lectura de los programas escritos en lenguaje Willy*.

Es importante tener en cuenta que se tomaron ciertas decisiones dentro de las precedencias del interpretador para evitar ambiguedades, entre ellas:

La instrucción:

`if x then if x then y else z`

es tomada de la siguiente forma

`if x then (if x then y else z)`

y no hay forma de que el else se refiera al if más externo ya que no hay paréntesis en la sintaxis de las instrucciones, y tampoco se toma en cuenta la identación de las instrucciones.


### Otras cosas importantes que resaltar:

- Todas las instrucciones dentro de los bloques de los mundos deben ir sin ; al final.

- Sólo las instrucciones dentro de los **bloques de las tareas y dentro de los bloques de begin end** tienen ; al final.

Esto está mal:

`if x then begin a; b; end; else if y then c;`

La forma correcta es: (sin el ; después del end)

`if x then begin a; b; end else if y then c;`

- No se pueden crear objetos ni booleanos con el mismo nombre el mundo.

- No se pueden crear funciones con el mismo nombre dentro de las tareas.

- Se pueden crear funciones dentro de funciones. (Y el nombre de las funciones pueden ser repetidas sí y sólo sí están dos niveles más internos de dónde se encuentra la función definida previamente).

- Todo lo que vaya a ser instanciado debe estar definido previamente.

- No se puede insertar objetos en la cesta de willy si no se definió la capacidad de la cesta previamente.

- Si el programa encuentra la instrucción terminate o se cumple el final goal la ejecución del task termina.


### Consideraciones en cuanto a la impresión:

- Las paredes están representadas por "/"

- Los objetos en el mundo están representados por "o","+","x","#" en ese orden, correspondiente al orden de creación del objeto

- Willy está representado por una w

- Si Willy está sobre algún objeto se representa con W


### Consideraciones en cuanto a la implementación:

- El interpretador ejecuta el programa de forma secuencial. Si se lee un task cuyo mundo no ha sido declarado previamente esto generaría un error.

- Si se definen dos task para un mismo mundo, el segundo task se va a ejecutar sobre el mundo resultante de haber aplicado el primer task, si y sólo si se hizo la ejecución de este primer task de forma correcta.

- Al leerse los mundos estos son creados y almacenados. Al leer los task, si el mundo al que hace referencia al task existe, este es ejecutado.

- Se recomienda declarar todos los mundos primero y luego los task, para que se realice una correcta ejecución de los mismos.

Para más información consultar: [Sobre la implementación](#sobre-la-implementación)


### Versiones anteriores
Versión 2.0
05/04/2020 

Actualizaciones:
- Se implementaron más archivos de prueba.
- Se realizó el árbol con las instrucciones para ser ejecutadas.
- Se acomodaron varios errores.

Versión 1.0
03/04/2020 

El proyecto no se encuentra terminado en su totalidad, sin embargo esta implementado:

- El lexer.
- El parser con sus correspondientes validaciones.
- La tabla de símbolos.
- Las clases World y Task para la implementación.


# Sobre la implementación

Este proyecto se dividió en 3 etapas:

En la primera fase del proyecto se implementó el análisis lexicográfico, el cual consiste en reconocer una entrada y dividirla en pequeños pedazos llamados tokens. 

Para realizar el análisis lexicográfico se utilizó una herramienta de construcción de lexer y parser llamada PLY.

La segunda etapa consistió en implementar un módulo sintáctico que utilice el módulo lexicográfico de la primera entrega. Este analizador debe aceptar o rechazar un programa dependiendo de si la entrada pertenece o no al lenguaje Willy*, que es el que utiliza nuestro robot para transitar en los mundos definidos en ese mismo lenguaje.

Y la última entrega se concentraba en terminar el interpretador del lenguaje y el simulador para que se realizara correctamente la ejecución del programa.

## Sobre el Lexer

Primero se definió una lista de palabras reservadas y una lista de tokens, que son las que se consideraron convenientes para los requerimientos del problema. 


Luego se definieron los tokens ignorados.

Muchas de las definiciones de tokens se hicieron con ayuda de las expresiones regulares, que nos permitían agrupar las cadenas de texto que se necesitaban.


También se implementaron dos listas, una de tokens válidos y otra de no válidos, para llevar un control de los tokens que se van formando a medida que se va leyendo el archivo inicial del programa, y de haber existencia de tokens no válidos puedan ser redirigidos a un manejador de errores.

El manejador de errores es importante porque en este lenguaje puede que hayan símbolos que no existan, y hay que manejarlos. Para ello se almacenó información pertinente de los tokens como la columna y línea donde se manifiesta el error.

Si el arreglo de tokens inválidos tiene algún elemento se muestra dicho error en pantalla y termina la ejecución.

## Sobre el Parser

Para la implementación del Parser primero se tuvo que entender cómo funciona el constructor de sintaxis que provee PLY, este se denomina yacc, y toma un conjunto de definiciones y las convierte en la gramática de nuestro lenguaje. La forma que tienen las definiciones presentes en este módulo se asemejan a las vistas en clase de Traductores.

El diseño de esta gramática comprende la forma en que se determina si un programa es correcto o no en el mundo de Willy. Para ello se utilizaron las especificaciones del mundo, y se buscó generalizar reglas que permitan que con símbolos terminales (los tokens obtenidos de la etapa del lexer) y los no terminales representados por las definiciones en el parser se pueda determinar la forma que van a tener las instrucciones dentro de Willy*. 

## Sobre el Interpretador

Se utilizó el modulo parser.py para implementar el interpretador ahí mismo.

Inicialmente se creó una **pila de símbolos** en donde se almacenan los distintos identificadores (ids) que son utilizados para cada mundo, tarea, variable booleana, nombre de función, objeto, etc. Esto con el objetivo de mantener un control de identificadores, y verificar que se utilicen correctamente; por ejemplo, no instanciar objetos que no fueron previamente definidos, o no definir dos funciones con el mismo nombre, incluso verificar que no existan dos mundos con el mismo nombre.

Este interpretador ejecuta el programa de forma secuencial. Si se lee un task cuyo mundo no ha sido declarado previamente esto generaría un error.


### Interpretar los mundos

Se creó una clase mundo con ciertos métodos y a partir del parser estos fueron invocados para así tener registradas las características del mismo y poder mostrarlo.

Para esta etapa se crearon también algunos controladores en el parser para asegurar que la asignación de atributos del mundo esten correctas. Por ejemplo, detectar si se tiene un mundo de tamaño 1x1, no construir paredes en la columna 3.

### Interpretar las tareas 

Se aprovechó la estructura del parser para crear nodos (estructuras que tienen un tipo e hijos), para que al ejecutar el parser la creación de nodos se hiciera recursivamente para así obtener una estructura de árbol con todas las instrucciones, similar a un árbol de derivación.

A partir de esta estructura se crearon varios métodos para manejar los nodos (especificadas en la parte de sobre el simulador)


## Sobre el Simulador

El simulador, quién es el encargado de la ejecución de las instrucciones del programa, fue implementado como una función dentro de la clase Node. Esta función tiene el nombre de executeMyTask() y todas las funciones que esta utiliza se encuentran dentro de la clase Node y la clase Task.

- Funciones a resaltar de Node:

    + finalGoalValue(): Para saber el valor booleano del final goal definido para cada mundo.

    + boolValue(): Para saber el valor booleano de las condiciones creadas en la tarea.

    + executeMyTask(): Quién es la función responsable de que se ejecuten todas las instrucciones de forma correcta dentro de Willy*. Esta utiliza la estructura de nodo para llamarse recursivamente y así ir recorriendo las instrucciones una a una.

    + timer(): Quién es la responsable de que las instrucciones se vayan ejecutando paso a paso (con la opción -a|--automatico) o con la tecla enter (con la opción -m|--manual).

- En la clase Task es en dónde se tiene la especificación de las instrucciones ejecutadas en executeMyTask().


# Archivos de Prueba

Todos estos se encuentran dentro del directorio llamado Pruebas


### PickStars.txt

:robot: :star: 

PickStars en un programa en lenguaje Willy que consta de un mundo llamado sky con dimensiones 8 x 9 con estrellas.

El objetivo es que Willy logre llegar a la posición final con 3 estrellas en su cesta.

### WillyCleanItsRoom.txt

:shirt: :blue_book: :computer:

Este es un programa que tiene un mundo llamado room con dimensiones 4 x 5 que representa el cuarto de una persona.

El objetivo de este es que Willy recoja su cuarto colocando su celular, su laptop y los libros en su mesa de trabajo (en donde está inicialmente su laptop) y que coloque toda la ropa sucia en la cesta de la ropa sucia.

### EatClean.txt

:cherries: :green_apple: :pizza:

Este programa contiene un mundo con comida saludable y comida no saludable.
Willy con un caminar sencillo recorre todo el mundo.

El final goal es llegar al final comiendose todas las frutas y no comiendose las pizzas.

### WriteFirstLetterOfMyName.txt

:pencil2: :pencil:

Aquí hay dos mundos en donde Willy escribe la primera letra de su nombre (W) en dimensiones distintas.

### ComesHappyToUni.txt

:smile: :expressionless: :triumph:

Este programa contiene un mundo que representa la ida a la universidad.
Por cada semaforo o señalización que Willy se encuentra lo pone de mal humor.
Por cada vez que sintoniza una canción en la radio que le gusta le mejora el humor.
¿Willy llegará de buen humor a la uni?

### WillyScan.txt 

:dart: :trophy:

Es un programa que simula un mundo 20 x 20 con vidas y objetos dañinos.
Willy tiene 5 vidas inicialmente y debe llegar a la meta sin quedarse sin vidas.

### EsferasDelDragon.txt

:dragon_face: :crystal_ball:

Es un programa que se encarga de recorrer laberitos con un set de muros y una esfera de dragon al final, el poder esta e que willy siempre llegue al final encontrando la esfera del dragon de forma dinamica
a manera de que permita cambios de los muros del mundo e igual se puedan mover


### Laberinto.txt

:fearful: :gem: :triangular_flag_on_post:

Es un porgrama que se encarga de recorrer laberitos con un set de muros una salida, 
La idea consiste en jugar con el ser de WALL dentro del o los mundos y permita que willy llegue al final con el task que existe

### TicTacToe.txt

:negative_squared_cross_mark: :o2:

La popular vieja en una forma estatica, a manera de que se permita jugar manipulando en task paso a paso  
Y willy sea capaz de ganar tanto con  O ó X

### Otros

Se dejaron también otros archivos de prueba que se utilizaron para probar el correcto funcionamiento de Willy.
 

# Conclusión

Para desarrollar un interpretador correctamente es importante realizarlo paso a paso. Primero definir cuáles van a ser las palabras que formaran parte del lenguaje, luego definir la estructura sintáctica que tendrán las instrucciones, para luego de haber verificado eso se pueda implementar la ejecución de un programa escrito en ese lenguaje.

Para Willy se necesitaron estructuras como la pila de símbolos porque en el mundo se podían definir variables y funciones, y se necesitaba tener un control de eso.

Otra estructura importante que se utilizó fue la del árbol que es la responsable de que la ejecución de las tareas pueda realizarse de forma correcta. Sin embargo este no se puede crear de forma correcta si no se tiene una buena gramática (que no sea ambigua ) que cree la estructura.

Para finalizar es importante comentar que esto fue posible gracias a dividir la tarea de crear el interpretador en pequeñas etapas e ir resolviendo cada una de ellas para así lograr el resultado final y darle vida a Willy.

:robot: :speech_balloon: *- Hello, World! -* 
