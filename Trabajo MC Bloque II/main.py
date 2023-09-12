from flask import Flask, render_template, make_response, request, jsonify
from sympy import *
import numpy as np

import os
import sys
import json


if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=template_folder)
else:
    app = Flask(__name__)

#####   Iniciamos la aplicación   #####"

#Variables globales accesibles desde cualquier función
x, y = symbols('x,y')

@app.route('/')
def inicializacion():
    #Inicializamos la página
    #Cargamos unos valores por defecto

    #Sistema número 4
    #fx = "a - x^2 +b*y, x" mapa de Henón para pruebas
    #no reconoce la función abs para realizar el valor absoluto
    #por tanto, tampoco podemos implementar el signo: x / |x|
    fxy = "y + sign(x)*sqrt(b*x - c), a - x".split(',') 
    gx = sympify(fxy[0])
    gy = sympify(fxy[1])

    #n => número de iteraciones
    n=5000
    #m => iteraciones finales
    m=0

    #x0, y0 => parametros iniciales
    x0 = 0
    y0 = 1

    #dinámica inicial sin calcular
    puntos_fijos = ()
    estabilidad = []
    matrizJacobiana = []
    autovalores = []
    n_Lyapunov = []
    exp_Lyapunov = []

    return render_template("index.html", gx=gx, gy=gy, n=n, m=m, x0=x0, y0=y0, puntos_fijos=puntos_fijos, estabilidad=estabilidad, 
    matrizJacobiana=matrizJacobiana, autovalores=autovalores, n_Lyapunov=n_Lyapunov, exp_Lyapunov=exp_Lyapunov)



@app.route('/dinamica')
def funciones():

    try:

        #Actualizamos los valores de cada función con los valores dados por parámetros
        fxy = request.args.get('input').split(',')
        valores = json.loads(request.args.get('values'))

        #Valores: x=?, y=?, a=?, b=?, c=? 
        print(f"* Valores: {valores}")
        print(f"* fx: {fxy[0]}")
        print(f"* fy: {fxy[1]}")

        #Sacamos x,y para obtener las variables a,b,c
        valores.pop("x")
        valores.pop("y")
        
        #Intercambiamos (subs) los valores de a,b,c de la función f(x,y) por sus valores reales
        gx = sympify(fxy[0]).subs(valores)
        gy = sympify(fxy[1]).subs(valores)
        print(f"* f(x,y)={gx,gy}")

        #Extraemos el resto de variables necesarias
        x0 = float(request.args.get("x0"))
        y0 = float(request.args.get("y0"))

        n = int(request.args.get("n"))
        m = int(request.args.get("m"))

        print(f"* x0={x0}, y0={y0}")

        #Puntos fijos
        #Para resolver los puntos fijos: f(x,y) = (x,y)
        #f(x,y): se indica que el primer parámetro corresponde a x (Eq(gx,x)) y el segundo a y (Eq(gy,y))
        puntos_fijos = list(nonlinsolve([Eq(gx,x), Eq(gy,y)], (x,y)))
        #puntos_fijos = p_fijos(gx, gy)
        print(f"* Puntos fijos: {puntos_fijos}")

        #Estabilidad
        #Calculamos la estabilidad de los puntos fijos con la función f_estabilidad(f0,g0,p)
        estabilidad=f_estabilidad(gx,gy,puntos_fijos)
        print(f"* Estabilidad: {estabilidad}")

        #Matriz Jacobiana
        #Matrix([gx, gy]).jacobian(Matrix([x,y])) nos devuelve la matriz Jacobiana de tipo Matrix
        #La convertimos en lista para iterar sobre ella
        mj = Matrix([gx, gy]).jacobian(Matrix([x,y]))
        matrizJacobiana = mj.tolist()
        print(f"* Matriz Jacobiana: {matrizJacobiana}")

        #Autovalores
        autovalores = [list(mj.subs({x:p[0], y:p[1]}).eigenvals().keys()) for p in puntos_fijos]
        print(f"* Autovalores: {autovalores}")

        #Número de Lyapunov
        n_Lyapunov = f_lyapunov(gx,gy,x0,y0)
        print(f"* Números de Lyapunov: {n_Lyapunov}")

        #Exponente de Lyapunov
        exp_Lyapunov = list(map(lambda x:ln(x), n_Lyapunov))
        print(f"* Exponentes de Lyapunov: {exp_Lyapunov}")

        return render_template('dinamica.html', puntos_fijos=puntos_fijos, estabilidad=estabilidad, matrizJacobiana=matrizJacobiana, 
        autovalores=autovalores, n_Lyapunov=n_Lyapunov, exp_Lyapunov=exp_Lyapunov)
    
    except Exception as ex:
        #dinámica inicial sin calcular
        puntos_fijos = ()
        estabilidad = []
        matrizJacobiana = []
        autovalores = []
        n_Lyapunov = []
        exp_Lyapunov = []
        error = "Se produjo un error!"

        return render_template("dinamica.html", gx=gx, gy=gy, n=n, m=m, x0=x0, y0=y0, puntos_fijos=puntos_fijos, estabilidad=estabilidad, 
        matrizJacobiana=matrizJacobiana, autovalores=autovalores, n_Lyapunov=n_Lyapunov, exp_Lyapunov=exp_Lyapunov, error=error)



def f_estabilidad(gx, gy, p_fijos):
    ls = list()
    Df = Matrix([gx, gy]).jacobian(Matrix([x,y]))
    for p in p_fijos:
        #Al aplicar el método "eigenvals" de la librería Sympy, este nos devuelve un diccionario de los autovalores y su multiplicidad
        #Para obtener los autovalores, accedemos a la clave del diccionario
        autovalores=list(Df.subs({x:p[0], y:p[1]}).eigenvals().keys())

        #Contemplamos la posibilidad de valores imaginarios
        if im(autovalores[0]) != 0:
            a = re(autovalores[0])
            b = im(autovalores[0])
            r = sqrt((a**2) + (b**2))
            print(f"* Módulo de autovalor[0]: {r}")
            if abs(r) < 1:
                ls.append((p, "punto atractivo (sumidero)"))
            else:
                ls.append((p, "punto repulsivo (fuente)"))
        
        elif len(set(autovalores)) == 2 and im(autovalores[1]) != 0:
            a = re(autovalores[1])
            b = im(autovalores[1])
            r = sqrt((a**2) + (b**2))
            print(f"* Módulo de autovalor[1]: {r}")
            if abs(r) < 1:
                ls.append((p, "punto atractivo (sumidero)"))
            else:
                ls.append((p, "punto repulsivo (fuente)")) 
                
        else:

            # 2 autovalores λ1 y λ2
            if len(set(autovalores)) == 2:
                #Caso 1:
                #Si ambos autovalores en valor absoluto son menores que 1, nos encontramos antes un punto atractivo o sumidero: |λ1|,|λ2| < 1
                if (abs(autovalores[0])<1 and abs(autovalores[1])<1):
                    ls.append((p, "punto atractivo (sumidero)"))

                #Caso 2:
                #Si ambos autovalores en valor absoluto son mayores que 1, punto repulsivo o fuente: |λ1|,|λ2| > 1
                elif (abs(autovalores[0])>1 and abs(autovalores[1])>1):
                    ls.append((p, "punto repulsivo (fuente)"))

                #Caso 3:
                #Si un autovalor es mayor que 1 en valor absoluto |λ1| > 1 y el otro es menor que 1 en valor absoluto |λ2| < 1; nos encontramos ante un punto de silla
                elif (abs(autovalores[0])>1 and abs(autovalores[1])<1):
                    ls.append((p, "punto de silla"))

                
            # 1 autovalor λ1
            elif len(set(autovalores)) == 1:
                #Caso 1:
                #|λ1|<1, punto atractivo o sumidero
                if (abs(autovalores[0])<1):
                    ls.append((p, "punto atractivo (sumidero)"))

                #Caso 2:
                #|λ1|>1, punto repulsivo o fuente
                elif (abs(autovalores[0])>1):
                    ls.append((p, "punto repulsivo (fuente)"))

    
    return ls


def f_lyapunov(gx, gy, x0, y0):
    m = Matrix([gx, gy])
    fx = m.diff(x)
    fy = m.diff(y)
    A = Matrix([[fx, fy]])
    A_t = A.transpose()
    return list(map(lambda x: sqrt(x), list((A*A_t).subs({x: x0, y: y0}).eigenvals().keys())))
            

if __name__ == '__main__':
    app.run(host="localhost", port=8080)

    



