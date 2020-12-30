from analizer.abstract import expression as exp

class ErrorOperatorExpression(exp.Expression):
    """
    Reporta error de operador
    """

    def __init__(self, operator, row, column):
        exp.Expression.__init__(self, row, column)
        self.operator = operator
        self.error = "No se pudo encontrar el operador: " + operator
        self.type = exp.ERROR.OPERATORERROR

    def execute(self, environment):
        print(self.error)
