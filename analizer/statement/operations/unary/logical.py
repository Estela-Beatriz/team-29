from analizer.abstract.expression import Expression, TYPE, list_errors, comps
from analizer.reports import Nodo
from analizer.statement.expressions import primitive
import pandas as pd


class Logical(Expression):
    """
    Esta clase contiene las expresiones booleanas unarias.
    """

    def __init__(self, exp, operator, row, column):
        super().__init__(row, column)
        self.exp = exp
        self.operator = operator
        if operator == "NOT":
            self.temp = str(operator) + " " + exp.temp
        else:
            self.temp = exp.temp + " " + comps.get(operator)

    def execute(self, environment):
        exp = self.execute(environment)
        operator = self.operator
        try:
            if type != TYPE.BOOLEAN:
                raise TypeError
            if isinstance(exp.value, pd.core.series.Series):
                if operator == "NOT":
                    value = ~exp.value
                elif operator == "ISTRUE":
                    value = exp.value == True
                elif operator == "ISFALSE":
                    value = exp.value == False
                elif operator == "ISUNKNOWN":
                    value = exp.value == None
                elif operator == "ISNOTTRUE":
                    value = exp.value != True
                elif operator == "ISNOTFALSE":
                    value = exp.value != False
                elif operator == "ISNOTUNKNOWN":
                    value = exp.value != None
                else:
                    raise TypeError
            else:
                if operator == "NOT":
                    value = not exp.value
                elif operator == "ISTRUE":
                    value = exp.value == True
                elif operator == "ISFALSE":
                    value = exp.value == False
                elif operator == "ISUNKNOWN":
                    value = exp.value == None
                elif operator == "ISNOTTRUE":
                    value = exp.value != True
                elif operator == "ISNOTFALSE":
                    value = exp.value != False
                elif operator == "ISNOTUNKNOWN":
                    value = exp.value != None
                else:
                    raise TypeError
            return primitive.Primitive(
                TYPE.BOOLEAN, value, self.temp, self.row, self.column
            )
        except TypeError:
            raise list_errors.append(
                "Error: 42883: la operacion no existe entre: "
                + str(type)
                + " y el operador "
                + str(operator)
                + "\n En la linea: "
                + str(self.row)
            )
        except:
            raise list_errors.append(
                "Error: XX000: Error interno (Binary Aritmethic Operation)"
                + "\n En la linea: "
                + str(self.row)
            )

    def dot(self):
        n1 = self.dot()
        new = Nodo.Nodo(self.operator)
        new.addNode(n1)
        return new