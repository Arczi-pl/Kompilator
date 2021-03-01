#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import ply.lex as lex

class Lexer(object):
    tokens = [
    "PLUS", "MINUS", "MNOZENIE", "DZIELENIE", "MODULO",     # dzialania: + - * / %
    "EQ", "NE", "LE", "GE", "LT", "GT",                     # operatory: = != < > <= >=
    "PRZYPISZ",                                             # przypisanie: :=
    "LEWY", "DWUKROPEK", "PRAWY",                           # tablica: ( : )
    "ZMIENNA", "SREDNIK", "PRZECINEK", "LICZBA",
    "DECLARE", "BEGIN", "END", 
    "IF", "THEN", "ELSE", "ENDIF",
    "WHILE", "DO", "ENDWHILE",
    "REPEAT", "UNTIL",           
    "FOR", "FROM", "TO", "DOWNTO", "ENDFOR",
    "READ", "WRITE",
    ]

    t_ignore = " \t"
    t_PLUS = r"\+"
    t_MINUS = r"-"
    t_MNOZENIE = r"\*"
    t_DZIELENIE = r"/"
    t_MODULO = r"%"
    t_EQ = r"="
    t_NE = r"!="
    t_LE = r"<"
    t_GE = r">"
    t_LT = r"<="
    t_GT = r">="
    t_PRZYPISZ = r":="
    t_LEWY = r"\("
    t_DWUKROPEK = r":"
    t_PRAWY = r"\)"
    t_DECLARE = r"DECLARE"
    t_BEGIN = r"BEGIN"
    t_END = r"END"
    t_IF = r"IF"
    t_THEN = r"THEN"
    t_ELSE = r"ELSE"
    t_ENDIF = r"ENDIF"
    t_WHILE = "WHILE"
    t_DO = "DO"
    t_ENDWHILE = "ENDWHILE"
    t_REPEAT = r"REPEAT"
    t_UNTIL = r"UNTIL"
    t_FOR = "FOR"
    t_FROM = "FROM"
    t_TO = "TO"
    t_DOWNTO = "DOWNTO"
    t_ENDFOR = "ENDFOR"
    t_READ = "READ"
    t_WRITE = "WRITE"
    t_ZMIENNA = r"[_a-z]+"
    t_SREDNIK = r";"
    t_PRZECINEK = r","

    def t_komentarz(self, t):
        r"\[[^\]]*\]"
        licznik_linii = 0
        for znak in t.value:
            if znak == "\n":
                licznik_linii += 1
        t.lexer.lineno += licznik_linii

    def t_LICZBA(self, t):
        r"[0-9]+"
        t.value = int(t.value)
        return t

    def t_nowa_linia(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        self.wyrzuc_blad("Błąd: Niepoprawny znak \"" + str(t.value[0]) + "\"" + " [Linia: " + str(t.lineno) +"]")

    def __init__(self):
        self.lexer = lex.lex(module=self, debug=0)

    def wyrzuc_blad(self, tresc):
        print(tresc)
        exit(-1)

    