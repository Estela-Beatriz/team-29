from abc import abstractmethod
from analizer.abstract.expression import Expression
from analizer.statement.expressions.tablle_all import TableAll
import sys

sys.path.append("../../..")
from storage.storageManager import jsonMode
from analizer.typechecker.Metadata import Struct
from analizer.typechecker import Checker
import pandas as pd
from analizer.symbol.symbol import Symbol
from analizer.symbol.environment import Environment
from analizer.reports import Nodo
from analizer.reports import AST


ast = AST.AST()
root = None

envVariables = []


# carga de datos
Struct.load()

# variable encargada de almacenar la base de datos a utilizar
dbtemp = ""
# listas encargadas de almacenar los errores semanticos
syntaxPostgreSQL = list()
semanticErrors = list()


def makeAst(root):
    ast.makeAst(root)


class Instruction:
    """
    Esta clase representa una instruccion
    """

    def __init__(self, row, column) -> None:
        self.row = row
        self.column = column

    @abstractmethod
    def execute(self, environment):
        """
        Metodo que servira para ejecutar las expresiones
        """


class SelectParams(Instruction):
    def __init__(self, params, row, column):
        Instruction.__init__(self, row, column)
        self.params = params

    def execute(self, environment):
        pass


class Select(Instruction):
    def __init__(
        self,
        params,
        fromcl,
        wherecl,
        groupbyCl,
        havingCl,
        limitCl,
        distinct,
        row,
        column,
    ):
        Instruction.__init__(self, row, column)
        self.params = params
        self.wherecl = wherecl
        self.fromcl = fromcl
        self.groupbyCl = groupbyCl
        self.havingCl = havingCl
        self.limitCl = limitCl
        self.distinct = distinct

    def execute(self, environment):
        try:
            newEnv = Environment(environment, dbtemp)
            global envVariables
            envVariables.append(newEnv)
            self.fromcl.execute(newEnv)
            if self.wherecl != None:
                self.wherecl.execute(newEnv)
            if self.groupbyCl != None:
                newEnv.groupCols = len(self.groupbyCl)
            groupDf = None
            groupEmpty = True
            if self.params:
                params = []
                for p in self.params:
                    if isinstance(p, TableAll):
                        result = p.execute(newEnv)
                        for r in result:
                            params.append(r)
                    else:
                        params.append(p)
                labels = [p.temp for p in params]
                if self.groupbyCl != None:
                    value = []
                    for i in range(len(params)):
                        ex = params[i].execute(newEnv)
                        val = ex.value
                        newEnv.types[labels[i]] = ex.type
                        # Si no es columna de agrupacion
                        if i < len(self.groupbyCl):
                            if not (
                                isinstance(val, pd.core.series.Series)
                                or isinstance(val, pd.DataFrame)
                            ):
                                nval = {
                                    val: [
                                        val for i in range(len(newEnv.dataFrame.index))
                                    ]
                                }
                                nval = pd.DataFrame(nval)
                                val = nval
                            newEnv.dataFrame = pd.concat(
                                [newEnv.dataFrame, val], axis=1
                            )
                        else:
                            if groupEmpty:
                                countGr = newEnv.groupCols
                                # Obtiene las ultimas columnas metidas (Las del group by)
                                df = newEnv.dataFrame.iloc[:, -countGr:]
                                cols = list(df.columns)
                                groupDf = df.groupby(cols).sum().reset_index()
                                groupDf = pd.concat([groupDf, val], axis=1)
                                groupEmpty = False
                            else:
                                groupDf = pd.concat([groupDf, val], axis=1)
                    if groupEmpty:
                        countGr = newEnv.groupCols
                        # Obtiene las ultimas columnas metidas (Las del group by)
                        df = newEnv.dataFrame.iloc[:, -countGr:]
                        cols = list(df.columns)
                        groupDf = df.groupby(cols).sum().reset_index()
                        groupEmpty = False
                else:
                    value = [p.execute(newEnv) for p in params]
                    for j in range(len(labels)):
                        newEnv.types[labels[j]] = value[j].type
                        newEnv.dataFrame[labels[j]] = value[j].value
            else:
                value = [newEnv.dataFrame[p] for p in newEnv.dataFrame]
                labels = [p for p in newEnv.dataFrame]
            if value != []:
                if self.wherecl == None:
                    df_ = newEnv.dataFrame.filter(labels)
                    if self.limitCl:
                        df_ = self.limitCl.execute(df_, newEnv)
                    if self.distinct:
                        return [df_.drop_duplicates(), newEnv.types]
                    return [df_, newEnv.types]
                w2 = newEnv.dataFrame.filter(labels)
                # Si la clausula WHERE devuelve un dataframe vacio
                if w2.empty:
                    return None
                df_ = w2
                if self.limitCl:
                    df_ = self.limitCl.execute(df_, newEnv)
                if self.distinct:
                    return [df_.drop_duplicates(), newEnv.types]
                return [df_, newEnv.types]
            else:
                newNames = {}
                i = 0
                for (columnName, columnData) in groupDf.iteritems():
                    newNames[columnName] = labels[i]
                    i += 1
                groupDf.rename(columns=newNames, inplace=True)
                df_ = groupDf
                if self.limitCl:
                    df_ = self.limitCl.execute(df_, newEnv)
                if self.distinct:
                    return [df_.drop_duplicates(), newEnv.types]
                return [df_, newEnv.types]
        except:
            syntaxPostgreSQL.append("Error: P0001: Error en la instruccion SELECT")

    def dot(self):
        new = Nodo.Nodo("SELECT")
        paramNode = Nodo.Nodo("PARAMS")
        new.addNode(paramNode)
        if self.distinct:
            dis = Nodo.Nodo("DISTINCT")
            new.addNode(dis)
        if len(self.params) == 0:
            asterisco = Nodo.Nodo("*")
            paramNode.addNode(asterisco)
        else:
            for p in self.params:
                paramNode.addNode(p.dot())
        new.addNode(self.fromcl.dot())
        if self.wherecl != None:
            new.addNode(self.wherecl.dot())

        if self.groupbyCl != None:
            gb = Nodo.Nodo("GROUP_BY")
            new.addNode(gb)
            for g in self.groupbyCl:
                gb.addNode(g.dot())
            if self.havingCl != None:
                hv = Nodo.Nodo("HAVING")
                new.addNode(hv)
                hv.addNode(self.havingCl.dot())

        if self.limitCl != None:
            new.addNode(self.limitCl.dot())

        return new


class FromClause(Instruction):
    """
    Clase encargada de la clausa FROM para la obtencion de datos
    """

    def __init__(self, tables, aliases, row, column):
        Instruction.__init__(self, row, column)
        self.tables = tables
        self.aliases = aliases

    def crossJoin(self, tables):
        if len(tables) <= 1:
            return tables[0]
        for t in tables:
            t["____tempCol"] = 1

        new_df = tables[0]
        i = 1
        while i < len(tables):
            new_df = pd.merge(new_df, tables[i], on=["____tempCol"])
            i += 1

        new_df = new_df.drop("____tempCol", axis=1)
        return new_df

    def execute(self, environment):
        tempDf = None
        for i in range(len(self.tables)):
            exec = self.tables[i].execute(environment)
            data = exec[0]
            types = exec[1]
            if isinstance(self.tables[i], Select):
                newNames = {}
                subqAlias = self.aliases[i]
                for (columnName, columnData) in data.iteritems():
                    colSplit = columnName.split(".")
                    if len(colSplit) >= 2:
                        newNames[columnName] = subqAlias + "." + colSplit[1]
                        types[subqAlias + "." + colSplit[1]] = columnName
                    else:
                        newNames[columnName] = subqAlias + "." + colSplit[0]
                        types[subqAlias + "." + colSplit[0]] = columnName
                data.rename(columns=newNames, inplace=True)
                environment.addVar(subqAlias, subqAlias, "TABLE", self.row, self.column)
            else:
                sym = Symbol(
                    self.tables[i].name,
                    None,
                    self.tables[i].row,
                    self.tables[i].column,
                )
                environment.addSymbol(self.tables[i].name, sym)
                if self.aliases[i]:
                    environment.addSymbol(self.aliases[i], sym)
            if i == 0:
                tempDf = data
            else:
                tempDf = self.crossJoin([tempDf, data])
            environment.dataFrame = tempDf
            try:
                environment.types.update(types)
            except:
                syntaxPostgreSQL.append(
                    "Error: P0001: Error en la instruccion SELECT clausula FROM"
                )
        return

    def dot(self):
        new = Nodo.Nodo("FROM")
        for t in self.tables:
            if isinstance(t, Select):
                n = t.dot()
                new.addNode(n)
            else:
                t1 = Nodo.Nodo(t.name)
                new.addNode(t1)
        for a in self.aliases:
            a1 = Nodo.Nodo(a)
            new.addNode(a1)
        return new


class TableID(Expression):
    """
    Esta clase representa un objeto abstracto para el manejo de las tablas
    """

    type_ = None

    def __init__(self, name, row, column):
        Expression.__init__(self, row, column)
        self.name = name

    def execute(self, environment):
        result = jsonMode.extractTable(dbtemp, self.name)
        if result == None:
            semanticErrors.append(
                [
                    "La tabla "
                    + str(self.name)
                    + " no pertenece a la base de datos "
                    + dbtemp,
                    self.row,
                ]
            )
            syntaxPostgreSQL.append(
                "Error: 42P01: la relacion "
                + dbtemp
                + "."
                + str(self.name)
                + " no existe"
            )
            return "FATAL ERROR TABLE ID"
        # Almacena una lista con con el nombre y tipo de cada columna
        lst = Struct.extractColumns(dbtemp, self.name)
        columns = [l.name for l in lst]
        newColumns = [self.name + "." + col for col in columns]
        df = pd.DataFrame(result, columns=newColumns)
        environment.addTable(self.name)
        tempTypes = {}
        for i in range(len(newColumns)):
            tempTypes[newColumns[i]] = lst[i].type
        return [df, tempTypes]


class WhereClause(Instruction):
    def __init__(self, series, row, column):
        super().__init__(row, column)
        self.series = series

    def execute(self, environment):
        filt = self.series.execute(environment)
        df = environment.dataFrame.loc[filt.value]
        environment.dataFrame = df.reset_index(drop=True)
        return df

    def dot(self):
        new = Nodo.Nodo("WHERE")
        new.addNode(self.series.dot())
        return new


class SelectOnlyParams(Select):
    def __init__(self, params, row, column):
        Instruction.__init__(self, row, column)
        self.params = params

    def execute(self, environment):
        try:
            newEnv = Environment(environment, dbtemp)
            global envVariables
            envVariables.append(newEnv)
            labels = []
            values = {}
            for i in range(len(self.params)):
                v = self.params[i].execute(newEnv)
                values[self.params[i].temp] = [v.value]
                labels.append(self.params[i].temp)
                newEnv.types[labels[i]] = v.type
            newEnv.dataFrame = pd.DataFrame(values)
            return [newEnv.dataFrame, newEnv.types]
        except:
            syntaxPostgreSQL.append("Error: P0001: Error en la instruccion SELECT")

    def dot(self):
        new = Nodo.Nodo("SELECT")
        paramNode = Nodo.Nodo("PARAMS")
        new.addNode(paramNode)
        if len(self.params) == 0:
            asterisco = Nodo.Nodo("*")
            paramNode.addNode(asterisco)
        else:
            for p in self.params:
                paramNode.addNode(p.dot())
        return new


class Assignment(Instruction):
    def __init__(self, id, value, row, column):
        Instruction.__init__(self, row, column)
        self.id = id
        self.value = value

    def execute(self, environment):
        if self.value != "DEFAULT":
            self.value = self.value.execute(environment).value
        return self

    def dot(self):
        new = Nodo.Nodo("=")
        idNode = Nodo.Nodo(str(self.id))
        new.addNode(idNode)
        new.addNode(self.value.dot())
        return new


class useDataBase(Instruction):
    def __init__(self, db, row, column):
        Instruction.__init__(self, row, column)
        self.db = db

    def execute(self, environment):
        dbs = jsonMode.showDatabases()
        if self.db in dbs:
            global dbtemp
            dbtemp = self.db
            return "Se cambio la base de datos a: " + dbtemp
        syntaxPostgreSQL.append(
            "Error: 42000: La base de datos " + self.db + " no existe"
        )
        semanticErrors.append(
            ["La base de datos " + str(self.db) + " no existe", self.row]
        )
        return "La base de datos: " + self.db + " no existe."

    def dot(self):
        new = Nodo.Nodo("USE_DATABASE")
        n = Nodo.Nodo(self.db)
        new.addNode(n)

        return new


class CheckOperation(Instruction):
    """
    Clase encargada de la instruccion CHECK que almacena la condicion
    a desarrollar en el CHECK
    """

    def __init__(self, exp1, exp2, operator, row, column):
        Instruction.__init__(self, row, column)
        self.exp1 = exp1
        self.exp2 = exp2
        self.operator = operator

    def execute(self, environment, value1, value2, type_):
        exp1 = self.exp1.execute(environment)
        exp2 = self.exp2.execute(environment)
        operator = self.operator
        if exp1.type == "ID" and exp2.type != "ID":
            value2 = exp2.value
        elif exp1.type != "ID" and exp2.type == "ID":
            value1 = exp1.value
        elif exp1.type == "ID" and exp2.type == "ID":
            pass
        else:
            syntaxPostgreSQL.append("Error: XX000: Error interno CHECK Operation")
            return None
        if type_ == "MONEY":
            value1 = str(value1)
            value2 = str(value2)
        try:
            comps = {
                "<": value1 < value2,
                ">": value1 > value2,
                ">=": value1 >= value2,
                "<=": value1 <= value2,
                "=": value1 == value2,
                "!=": value1 != value2,
                "<>": value1 != value2,
                "ISDISTINCTFROM": value1 != value2,
                "ISNOTDISTINCTFROM": value1 == value2,
            }
            value = comps.get(operator, None)
            if value == None:
                return Expression.ErrorBinaryOperation(
                    exp1.value, exp2.value, self.row, self.column
                )
            return value
        except:
            syntaxPostgreSQL.append("Error: XX000: Error interno CHECK")


class limitClause(Instruction):
    def __init__(self, num, offset, row, column) -> None:
        super().__init__(row, column)
        self.num = num
        self.offset = offset

    def execute(self, dataFrame, environment):
        temp = dataFrame
        if self.offset != None:
            temp = dataFrame[self.offset :]
        if self.num == "ALL":
            return temp
        return temp.head(self.num)

    def dot(self):
        new = Nodo.Nodo("LIMIT")
        numN = Nodo.Nodo(str(self.num))
        new.addNode(numN)
        if self.offset != None:
            off = Nodo.Nodo("OFFSET")
            new.addNode(off)
            offId = Nodo.Nodo(str(self.offset))
            off.addNode(offId)

        return new


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


def returnErrors():
    list_ = list()
    list_ = Checker.returnErrors()
    list_ += syntaxPostgreSQL
    return list_


def returnSemanticErrors():
    return semanticErrors