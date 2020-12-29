
from analizer.symbol.environment import Environment
from analizer.reports import Nodo
from analizer.abstract.instruction import Instruction
from analizer.abstract.instruction import dbtemp
from analizer.abstract.instruction import envVariables
from analizer.expressions.tablle_all import TableAll
from analizer.abstract.instruction import syntaxPostgreSQL

import pandas as pd

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
