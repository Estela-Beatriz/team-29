from analizer.reports import Nodo
from analizer.abstract.instruction import Instruction
from analizer.abstract.instruction import dbtemp
from analizer.abstract.instruction import semanticErrors
from analizer.abstract.instruction import syntaxPostgreSQL
from analizer.symbol.environment import Environment
from analizer.abstract.instruction import envVariables

import pandas as pd

class Union(Instruction):
    """
    Clase encargada de la instruccion CHECK que almacena la condicion
    a desarrollar en el CHECK
    """

    def __init__(self, s1, s2, row, column):
        Instruction.__init__(self, row, column)
        self.s1 = s1
        self.s2 = s2

    def execute(self, environment):
        newEnv = Environment(environment, dbtemp)
        global envVariables
        envVariables.append(newEnv)
        s1 = self.s1.execute(newEnv)
        s2 = self.s2.execute(newEnv)
        df1 = s1[0]
        df2 = s2[0]
        types1 = list(s1[1].values())
        types2 = list(s2[1].values())
        if len(df1.columns) != len(df2.columns):
            syntaxPostgreSQL.append(
                "Error: 42611: UNION definicion en numero de columnas invalida "
            )
            return "Error: El numero de columnas no coinciden"
        for i in range(len(types1)):
            if types1[i] != types2[i]:
                semanticErrors.append(
                    ["Error discrepancia de tipo de datos entre columnas", self.row]
                )
                syntaxPostgreSQL.append(
                    "Error: 42804: discrepancia de tipo de datos entre columnas "
                )
                return "Error: Los tipos de columnas no coinciden"
        df = pd.concat([df1, df2], ignore_index=True)
        return df

    def dot(self):
        new = Nodo.Nodo("UNION")
        new.addNode(self.s1.dot())
        new.addNode(self.s2.dot())
        return new


class Intersect(Instruction):
    """
    Clase encargada de la instruccion CHECK que almacena la condicion
    a desarrollar en el CHECK
    """

    def __init__(self, s1, s2, row, column):
        Instruction.__init__(self, row, column)
        self.s1 = s1
        self.s2 = s2

    def execute(self, environment):
        newEnv = Environment(environment, dbtemp)
        global envVariables
        envVariables.append(newEnv)
        s1 = self.s1.execute(newEnv)
        s2 = self.s2.execute(newEnv)
        df1 = s1[0]
        df2 = s2[0]
        types1 = list(s1[1].values())
        types2 = list(s2[1].values())
        if len(df1.columns) != len(df2.columns):
            syntaxPostgreSQL.append(
                "Error: 42611: INTERSEC definicion en numero de columnas invalida "
            )

            return "Error: El numero de columnas no coinciden"
        for i in range(len(types1)):
            if types1[i] != types2[i]:
                semanticErrors.append(
                    ["Error discrepancia de tipo de datos entre columnas", self.row]
                )
                syntaxPostgreSQL.append(
                    "Error: 42804: discrepancia de tipo de datos entre columnas "
                )
                return "Error: Los tipos de columnas no coinciden"
        df = df1.merge(df2).drop_duplicates(ignore_index=True)
        return df

    def dot(self):
        new = Nodo.Nodo("INTERSECT")
        new.addNode(self.s1.dot())
        new.addNode(self.s2.dot())
        return new


class Except_(Instruction):
    """
    Clase encargada de la instruccion CHECK que almacena la condicion
    a desarrollar en el CHECK
    """

    def __init__(self, s1, s2, row, column):
        Instruction.__init__(self, row, column)
        self.s1 = s1
        self.s2 = s2

    def execute(self, environment):
        newEnv = Environment(environment, dbtemp)
        global envVariables
        envVariables.append(newEnv)
        s1 = self.s1.execute(newEnv)
        s2 = self.s2.execute(newEnv)
        df1 = s1[0]
        df2 = s2[0]
        types1 = list(s1[1].values())
        types2 = list(s2[1].values())
        if len(df1.columns) != len(df2.columns):
            syntaxPostgreSQL.append(
                "Error: 42611: EXCEPT definicion en numero de columnas invalida "
            )
            return "Error: El numero de columnas no coinciden"
        for i in range(len(types1)):
            if types1[i] != types2[i]:
                semanticErrors.append(
                    ["Error discrepancia de tipo de datos entre columnas", self.row]
                )
                syntaxPostgreSQL.append(
                    "Error: 42804: discrepancia de tipo de datos entre columnas"
                )
                return "Error: Los tipos de columnas no coinciden"
        df = df1.merge(df2, how="outer", indicator=True).loc[
            lambda x: x["_merge"] == "left_only"
        ]
        del df["_merge"]
        return df

    def dot(self):
        new = Nodo.Nodo("EXCEPT")
        new.addNode(self.s1.dot())
        new.addNode(self.s2.dot())
        return new
