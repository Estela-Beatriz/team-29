from sys import path
from os.path import dirname as dir
from shutil import rmtree

path.append(dir(path[0]))

from analizer import grammar

dropAll = 0
if dropAll:
    print("Eliminando registros")
    rmtree("data")


s = """ 
USE test;
CREATE TABLE tbusuario (
    idusuario integer NOT NULL primary key,
	nombre varchar(50),
	apellido varchar(50),
	usuario varchar(15)  UNIQUE NOT NULL,
	password varchar(15) NOT NULL,
	fechacreacion date 
);
CREATE TABLE tbroles (
    idrol integer NOT NULL primary key,
	rol varchar(15)
);

DROP TABLE tbroles;

CREATE TABLE tbrol (
    idrol integer NOT NULL primary key,
	rol varchar(15)
);
"""
result = grammar.parse(s)
print(result)
result = grammar
# print(result[0].execute(None))
# print(result[1].execute(None))
# print(grammar.returnPostgreSQLErrors())
