# Tipos de datos primitivos
from analizer.expressions import primitive

# Identificadores
from analizer.expressions import identifiers

# Operaciones unarias
from analizer.operations.unary import arithmetic as UnaryArithmetic
from analizer.operations.unary import relational as UnaryRelational
from analizer.operations.unary import logical as UnaryLogical

# Operaciones binarias
from analizer.operations.binary import arithmetic as BinaryArithmetic
from analizer.operations.binary import logical as BinaryLogical
from analizer.operations.binary import relational as BinaryRelational
from analizer.operations.binary import string as BinaryString

# Operaciones ternarias
from analizer.operations.ternary import relational as TernaryRelational

# Funcion Extract
from analizer.functions import extract


def Primitive(type_, value, temp, row, column):
    return primitive.Primitive(type_, value, temp, row, column)


def Identifiers(table, name, row, column):
    return identifiers.Identifiers(table, name, row, column)


def UnaryArithmeticOperation(exp, operator, row, column):
    return UnaryArithmetic.Arithmetic(exp, operator, row, column)


def UnaryRelationalOperation(exp, operator, row, column):
    return UnaryRelational.Relational(exp, operator, row, column)


def UnaryLogicalOperation(exp, operator, row, column):
    return UnaryLogical.Logical(exp, operator, row, column)


def BinaryArithmeticOperation(exp1, exp2, operator, row, column):
    return BinaryArithmetic.Arithmetic(exp1, exp2, operator, row, column)


def BinaryLogicalOperation(exp1, exp2, operator, row, column):
    return BinaryLogical.Logical(exp1, exp2, operator, row, column)


def BinaryRelationalOperation(exp1, exp2, operator, row, column):
    return BinaryRelational.Relational(exp1, exp2, operator, row, column)


def BinaryStringOperation(exp1, exp2, operator, row, column):
    return BinaryString.String(exp1, exp2, operator, row, column)


def TernaryRelationalOperation(exp1, exp2, exp3, operator, row, column):
    return TernaryRelational.Relational(exp1, exp2, exp3, operator, row, column)


def ExtractDate(opt, type_, str, row, column):
    return extract.ExtractDate(opt, type_, str, row, column)


def ExtractColumnDate(opt, colData, row, column):
    return extract.ExtractColumnDate(opt, colData, row, column)