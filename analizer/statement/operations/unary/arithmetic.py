from analizer.abstract.expression import Expression, TYPE, list_errors
from analizer.reports import Nodo
from analizer.statement.expressions import primitive


class Arithmetic(Expression):
    """
    Esta clase recibe un parametro de expresion
    para realizar operaciones unarias
    """

    def __init__(self, exp, operator, row, column):
        super().__init__(row, column)
        self.exp = exp
        self.operator = operator
        self.temp = str(operator) + exp.temp

    def execute(self, environment):
        exp = self.execute(environment)
        operator = self.operator
        if type != TYPE.NUMBER:
            list_errors.append(
                "Error: 42883: la operacion no existe entre: "
                + str(operator)
                + " "
                + str(type)
                + "\n En la linea: "
                + str(self.row)
            )
            return ArithmeticError
        if operator == "+":
            value = exp.value
        elif operator == "-":
            value = exp.value * -1
        else:
            list_errors.append(
                "Error: 42883: la operacion no existe entre: "
                + str(operator)
                + " "
                + str(type)
                + "\n En la linea: "
                + str(self.row)
            )
            raise Exception
        return primitive.Primitive(TYPE.NUMBER, value, self.temp, self.row, self.column)

    def dot(self):
        n1 = self.dot()
        new = Nodo.Nodo(self.operator)
        new.addNode(n1)
        return new