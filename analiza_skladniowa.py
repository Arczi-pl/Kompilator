#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import ply.yacc as yacc

class Parser(object):
    def p_program_z_deklaracjami(self, p):
        '''program : DECLARE deklaracje BEGIN instrukcje END'''
        p[0] = ("program", p[2], p[4])

    def p_program_bez_deklaracji(self, p):
        '''program : BEGIN instrukcje END'''
        p[0] = ("program", [], p[2])

    def p_deklaracja_pojedyncza_zmienna(self, p):
        '''deklaracje : ZMIENNA'''
        zmienna = ("zmienna", p[1], p.lineno(1))
        p[0] = []
        p[0].append(zmienna)
        
    def p_deklaracja_wiele_zmiennych(self, p):
        '''deklaracje : deklaracje PRZECINEK ZMIENNA'''
        zmienna = ("zmienna", p[3], p.lineno(3))
        if p[1]:
            p[0] = p[1]
        else:
            p[0] = []
        p[0].append(zmienna)

    def p_deklaracja_pojedyncza_tablica(self, p):
        '''deklaracje : ZMIENNA LEWY LICZBA DWUKROPEK LICZBA PRAWY'''
        tablica = ("tablica", p[1], p[3], p[5], p.lineno(3))
        p[0] = []
        p[0].append(tablica)

    def p_deklaracja_wiele_tablic(self, p):
        '''deklaracje : deklaracje PRZECINEK ZMIENNA LEWY LICZBA DWUKROPEK LICZBA PRAWY'''
        tablica = ("tablica", p[3], p[5], p[7], p.lineno(3))
        if p[1]:
            p[0] = p[1]
        else:
            p[0] = []        
        p[0].append(tablica)

    def p_deklaracje_puste(self, p):
        "deklaracje : "
        self.wyrzuc_blad("Błąd: Puste pole deklaracji")

    def p_instrukcje(self, p):
        "instrukcje : instrukcje instrukcja"
        p[1].append(p[2])
        p[0] = p[1]

    def p_instrukcja(self, p):
        "instrukcje : instrukcja"
        p[0] = [p[1]]

    def p_instrukcja_przypisz(self, p):
        '''instrukcja : identyfikator PRZYPISZ wyrazenie SREDNIK'''
        p[0] = ("przypisz", p[1], p[3])

    def p_instrukcja_if_then_else(self, p):
        '''instrukcja : IF warunek THEN instrukcje ELSE instrukcje ENDIF'''
        p[0] = ("if_then_else", p[2], p[4], p[6])

    def p_instrukcja_if_then(self, p):
        "instrukcja : IF warunek THEN instrukcje ENDIF"
        p[0] = ("if_then", p[2], p[4])

    def p_instrukcja_while(self, p):
        "instrukcja : WHILE warunek DO instrukcje ENDWHILE"
        p[0] = ("while", p[2], p[4])

    def p_instrukcja_repeat_until(self, p):
        '''instrukcja : REPEAT  instrukcje  UNTIL  warunek SREDNIK'''
        p[0] = ("repeat_until", p[2], p[4])

    def p_instrukcja_for_to(self, p):
        '''instrukcja : FOR  ZMIENNA  FROM  wartosc TO  wartosc DO  instrukcje  ENDFOR'''
        p[0] = ("for_to", p[2], p[4], p[6], p[8], p.lineno(1))

    def p_instrukcja_for_downto(self, p):
        '''instrukcja : FOR  ZMIENNA  FROM  wartosc DOWNTO  wartosc DO  instrukcje  ENDFOR'''
        p[0] = ("for_downto", p[2], p[4], p[6], p[8], p.lineno(1))

    def p_instrukcja_read(self, p):
        "instrukcja : READ  identyfikator SREDNIK"
        p[0] = ("read",  p[2])

    def p_instrukcja_write(self, p):
        "instrukcja : WRITE wartosc SREDNIK"
        p[0] = ("write", p[2] )

    def p_wyrazenie_pojedyncze(self, p):
        "wyrazenie : wartosc"
        p[0] = ("wyrazenie", p[1])

    def p_wyrazenie_zlozone(self, p):
        '''wyrazenie : wartosc PLUS wartosc
                | wartosc MINUS wartosc
                | wartosc MNOZENIE wartosc
                | wartosc DZIELENIE wartosc
                | wartosc MODULO wartosc '''
        p[0] = ("wyrazenie", p[2], p[1], p[3])

    def p_warunek(self, p):
        '''warunek : wartosc EQ wartosc
                | wartosc NE wartosc
                | wartosc LE wartosc
                | wartosc GE wartosc
                | wartosc LT wartosc
                | wartosc GT wartosc'''
        p[0] = ("warunek", p[2], p[1], p[3])

    def p_wartosc(self, p):
        """wartosc : LICZBA
                 | identyfikator
        """
        p[0] = p[1]

    def p_id(self, p):
        '''identyfikator : ZMIENNA'''
        p[0] = ("zmienna", p[1], p.lineno(1))

    def p_id_tabablica_zmienna(self, p):
        '''identyfikator : ZMIENNA LEWY ZMIENNA PRAWY'''
        p[0] = ("tablica", p[1], p[3], p.lineno(1))

    def p_id_tabablica_liczba(self, p):
        '''identyfikator : ZMIENNA LEWY LICZBA PRAWY'''
        p[0] = ("tablica", p[1], p[3], p.lineno(1))

    def p_error(self, p):
        self.wyrzuc_blad("Błąd: niepoprawna składnia \"" + str(p.value) + "\" [linia " + str(p.lineno)+ "]")

    def __init__(self, lexer):
        self.lexer = lexer
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self, debug=0, write_tables=0)

    def parse(self, data):
        if data:
            drzewo_parsowania = self.parser.parse(data, self.lexer.lexer, 0, 0, None)
            if drzewo_parsowania[0] == "program":
                return drzewo_parsowania[1], drzewo_parsowania[2]
            else:
                self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")
        else:
            self.wyrzuc_blad("Błąd: pusty plik wejściowy")

    def wyrzuc_blad(self, tresc):
        print(tresc)
        exit(-1)


