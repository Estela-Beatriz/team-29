import sys
sys.path.append("../../..")
from storage.storageManager import jsonMode
from analizer.typechecker.Metadata import Struct
from analizer.symbol.environment import Environment
from analizer.reports import Nodo
from analizer.abstract import instruction as inst

envVariables = []


# carga de datos
Struct.load()

# variable encargada de almacenar la base de datos a utilizar
dbtemp = ""
# listas encargadas de almacenar los errores semanticos
syntaxPostgreSQL = list()
semanticErrors = list()
syntaxErrors = list()
class Update(inst.Instruction):
    def __init__(self, fromcl, values, wherecl, row, column):
        inst.Instruction.__init__(self, row, column)
        self.wherecl = wherecl
        self.fromcl = fromcl
        self.values = values

    def execute(self, environment):
        try:
            # Verificamos que no pueden venir mas de 1 tabla en el clausula FROM
            if len(self.fromcl.tables) > 1:
                syntaxErrors.append(["Error sintactico cerco e en ','", self.row])
                syntaxPostgreSQL.append(
                    "Error: 42601: Error sintactico cerca de , en la linea "
                    + str(self.row)
                )
                return "Error: syntax error at or near ','"
            newEnv = Environment(environment, dbtemp)
            global envVariables
            envVariables.append(newEnv)
            self.fromcl.execute(newEnv)
            value = [newEnv.dataFrame[p] for p in newEnv.dataFrame]
            labels = [p for p in newEnv.dataFrame]
            for i in range(len(labels)):
                newEnv.dataFrame[labels[i]] = value[i]
            if self.wherecl == None:
                w2 = newEnv.dataFrame.filter(labels)
            else:
                wh = self.wherecl.execute(newEnv)
                w2 = wh.filter(labels)
            # Si la clausula WHERE devuelve un dataframe vacio
            if w2.empty:
                return "Operacion UPDATE completada"
            # Logica para realizar el update
            table = self.fromcl.tables[0].name
            pk = Struct.extractPKIndexColumns(dbtemp, table)
            # Se obtienen las parametros de las llaves primarias para proceder a eliminar
            rows = []
            if pk:
                for row in w2.values:
                    rows.append([row[p] for p in pk])
            else:
                rows.append([i for i in w2.index])
            print(rows)
            # Obtenemos las variables a cambiar su valor
            ids = [p.id for p in self.values]
            values = [p.execute(newEnv).value for p in self.values]
            ids = Struct.getListIndex(dbtemp, table, ids)
            if len(ids) != len(values):
                return "Error: Columnas no encontradas"
            temp = {}
            for i in range(len(ids)):
                temp[ids[i]] = values[i]
            print(temp, rows)
            # TODO: La funcion del STORAGE esta bugueada
            bug = False
            for row in rows:
                result = jsonMode.update(dbtemp, table, temp, rows)
                if result != 0:
                    bug = True
                    break
            if bug:
                return ["Error: Funcion UPDATE del Storage", temp, rows]
            return "Operacion UPDATE completada"
        except:
            syntaxPostgreSQL.append("Error: P0001: Error en la instruccion UPDATE")

    def dot(self):
        new = Nodo.Nodo("UPDATE")
        new.addNode(self.fromcl.dot())
        assigNode = Nodo.Nodo("SET")
        new.addNode(assigNode)
        for v in self.values:
            assigNode.addNode(v.dot())
        new.addNode(self.wherecl.dot())
        return new