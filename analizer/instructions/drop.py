from analizer.abstract import instruction as inst
from analizer.typechecker.Metadata import Struct
from analizer.reports import Nodo
from storage.storageManager import jsonMode

class Drop(inst.Instruction):
    """
    Clase que representa la instruccion DROP TABLE and DROP DATABASE
    Esta instruccion es la encargada de eliminar una base de datos en el DBMS
    """

    def __init__(self, structure, name, exists):
        self.structure = structure
        self.name = name
        self.exists = exists

    def execute(self, environment):
        try:
            if self.structure == "TABLE":
                if inst.dbtemp != "":
                    valor = jsonMode.dropTable(inst.dbtemp, self.name)
                    if valor == 2:
                        inst.semanticErrors.append(
                            ["La base de datos " + str(inst.dbtemp) + " no existe", self.row]
                        )
                        inst.syntaxPostgreSQL.append(
                            "Error: 42000: La base de datos  "
                            + str(inst.dbtemp)
                            + " no existe"
                        )
                        return "La base de datos no existe"
                    if valor == 3:
                        inst.semanticErrors.append(
                            ["La tabla " + str(self.name) + " no existe", self.row]
                        )
                        inst.syntaxPostgreSQL.append(
                            "Error: 42P01: La tabla  " + str(self.name) + " no existe"
                        )
                        return "La tabla no existe en la base de datos"
                    if valor == 1:
                        inst.syntaxPostgreSQL.append("Error: XX000: Error interno")
                        return "Hubo un problema en la ejecucion de la sentencia DROP"
                    if valor == 0:
                        Struct.dropTable(inst.dbtemp, self.name)
                        return "DROP TABLE Se elimino la tabla: " + self.name
                inst.syntaxPostgreSQL.append("Error: 42000: Base de datos no especificada ")
                return "El nombre de la base de datos no esta especificado operacion no realizada"
            else:
                valor = jsonMode.dropDatabase(self.name)
                if valor == 1:
                    inst.syntaxPostgreSQL.append("Error: XX000: Error interno")
                    return "Hubo un problema en la ejecucion de la sentencia"
                if valor == 2:
                    inst.semanticErrors.append(
                        ["La base de datos " + inst.dbtemp + " no existe", self.row]
                    )
                    inst.syntaxPostgreSQL.append(
                        "Error: 42000: La base de datos  " + str(inst.dbtemp) + " no existe"
                    )
                    return "La base de datos no existe"
                if valor == 0:
                    Struct.dropDatabase(self.name)

                    return "Instruccion ejecutada con exito DROP DATABASE"
            inst.syntaxPostgreSQL.append("Error: XX000: Error interno DROPTABLE")
            return "Fatal Error: DROP TABLE"
        except:
            inst.syntaxPostgreSQL.append("Error: P0001: Error en la instruccion DROP")

    def dot(self):
        new = Nodo.Nodo("DROP")
        t = Nodo.Nodo(self.structure)
        n = Nodo.Nodo(self.name)
        new.addNode(t)
        new.addNode(n)
        return new

