from docplex.mp.model import Model
import docplex.mp.solution as Solucion
import csv

#-------------------------------------------------------------------------------
# Método que limpia los datos
#-------------------------------------------------------------------------------
def clean(row):
    nrow = []
    for i in row:
        #nrow.append(i)
        i = i.split("km")[0]
        nrow.append(float(i)) # Se cambia el tipo de dato
    return nrow
#-------------------------------------------------------------------------------
# Método que lee el archivo CSV
#-------------------------------------------------------------------------------
def read_file(src):
    rows = []
    with open(src, 'r') as file:
        reader = csv.reader(file, delimiter = ';')
        c = 1
        for row in reader:
            if c==1:
                row[0] = '0' #Reemplaza el primer valor por un 0
                nrow = clean(row) # se limpian los datos
                #print (nrow)
            c+=1
            nrow = clean(row)
            rows.append(nrow)
    return rows

#-------------------------------------------------------------------------------
# Método que multiplica las distancias en km por el costo total de pelos de fibra que se instalaran
#-------------------------------------------------------------------------------
def total_cost(datos):
    data_cost =[]
    for row in range(len(datos)):
        r = []
        for col in range(len(datos)):
            cost = datos[row][col] *202.8125 # ditancia * costo de cada pelo fibra km*dolar/(gbps*km)  ===> valor gbps
            r.append(cost)
        data_cost.append(r)
    return data_cost

#-------------------------------------------------------------------------------
# Método que resuelve el problema
#-------------------------------------------------------------------------------
def modelo(mdl, Costos, plantas, destinos, Arcos, Capacidad, Demanda):

    #Variable entera de cantidad a producir
    x=mdl.continuous_var_dict(Arcos,name='x')
    #Función objetivo
    mdl.minimize(mdl.sum(x[i, j]*Costos.get((i, j)) for i in plantas for j in destinos if j!=i))  # funcion obj

    # Primero restricción de capacidad
    for k in plantas:
        mdl.add_constraint(mdl.sum(x[(k,j)] for j in Demanda if j!=k)<=Capacidad[k])

    # Segundo restricción de demanda
    for k in Demanda:
        mdl.add_constraint(mdl.sum(x[(i,k)] for i in Capacidad if i!=k)>=Demanda[k])

    print(mdl.export_to_string())

    solucion = mdl.solve(log_output=True)
    mdl.get_solve_status()
    return solucion.display()


datos = read_file('./data/data.csv')
aCost = total_cost(datos)

plantas=[k for k in range(20)]
destinos=[k for k in range(20)]
Arcos =[(i,j) for i in plantas for j in destinos]

# Creando los diccionarios a utilizar en el modelo
Capacidad = {0: 0.03 * 147577,  # 147577
              1: 0.03 * 112449,  # 112449,
              2: 0.03 * 71258,
              3: 0.03 * 4397,
              4: 0.03 * 25947,
              5: 0.03 * 112449,  # 112449
              6: 0.03 * 31650,
              7: 0.03 * 6570,
              8: 0.03 * 20524,
              9: 0.03 * 16244,
              10: 0.03 * 6132,
              11: 0.03 * 7713,
              12: 0.03 * 19865,
              13: 0.03 * 16742,
              14: 0.03 * 3727,
              15: 0.03 * 8626,
              16: 0.03 * 4510,
              17: 0.03 * 7896,
              18: 0.03 * 1973,
              19: 0.03 * 1489
              }
Demanda = {
    0: 0.01 * 147577,  # 147577
    1: 0.01 * 112449,  # 112449
    2: 0.01 * 71258,
    3: 0.01 * 4397,
    4: 0.01 * 25947,
    5: 0.01 * 112449,  # 112449
    6: 0.01 * 31650,
    7: 0.01 * 6570,
    8: 0.01 * 20524,
    9: 0.01 * 16244,
    10: 0.01 * 6132,
    11: 0.01 * 7713,
    12: 0.01 * 19865,
    13: 0.01 * 16742,
    14: 0.01 * 3727,
    15: 0.01 * 8626,
    16: 0.01 * 4510,
    17: 0.01 * 7896,
    18: 0.01 * 1973,
    19: 0.01 * 1489
}
Costos = {(i, j): aCost[i][j] for i in range(len(aCost)) for j in range(len(aCost)) if j!=i}
mdl=Model('Transp')
modelo(mdl,Costos, plantas, destinos, Arcos, Capacidad, Demanda)

#-------------------------------------------------------------------------------
# Método que realiza el análisis de sensibilidad
#-------------------------------------------------------------------------------
n_restrict = mdl.number_of_constraints
restricts = [mdl.get_constraint_by_index(i) for i in range(n_restrict)]
print(restricts)
#Variables de holgura
holguras = mdl.slack_values(restricts)
print(holguras)

#-------------------------------------------------------------------------------
# Mostrando variables de Holgura por cada restricción
#-------------------------------------------------------------------------------
for index in range(n_restrict):
    print("La variable de holgura de la restricción " + str(restricts[index]) + " es " + str(holguras[index]))

#Precios duales
precio_dual = mdl.dual_values(restricts)

# Mostrando variables de Holgura por cada restricción
for index in range(n_restrict):
    print("El precio dual de la restricción " + str(restricts[index]) + " es " + str(precio_dual[index]))

#---------------------------------------------------------------------------------------------------
#Reporte de Sensibilidad, como se obtiene la sensibilidad del lado derecho o de la función objetivo en Cplex.
#----------------------------------------------------------------------------------------------------
cpx = mdl.get_engine().get_cplex()
coeff = cpx.solution.sensitivity.objective() #Coeficientes
ld = cpx.solution.sensitivity.rhs() #lado derecho

#lista de variables
var_list = []
for i in range(20):
    for j in range(20):
        var = mdl.get_var_by_name('x_'+str(i)+'_'+str(j))
        var_list.append(var)
#-------------------------------------------------------------------------------
# Sensibilidad de la función Objetivo
#-------------------------------------------------------------------------------
print(" ")
print(20*"-"+"Análisis - Sensibilidad Función Objetivo"+"-"*20)
print(" ")

for n in range(len(var_list)):
    print("La variable " + str(var_list[n]) + " " + str(coeff[n]))

#-------------------------------------------------------------------------------
# Restricciones y sensibilidad lado derecho
#-------------------------------------------------------------------------------
print(" ")
print(20*"-"+"Análisis - Restricciones y  Sensibilidad Lado Derecho"+"-"*20)
print(" ")

for n in range(n_restrict):
    print("La Restricción " + str(restricts[n]) + " " + str(ld[n]))
