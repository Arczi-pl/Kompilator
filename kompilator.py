#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import sys
from analiza_leksykalna import Lexer
from analiza_skladniowa import Parser
from analiza_semantyczna import AnalizatorSymantyczny as AS
from optymalizator import Optymalizator as OPT
from graf_przeplywu_sterowania import GrafPrzeplywuSterowania as GPS
from generator_kodu import GeneratorKoduMaszynyWirtualnej as GKMW


def wyrzuc_blad(tresc):
    print(tresc)
    exit(-1)


def main():
    if len(sys.argv) == 3:
        plik_z_programem = sys.argv[1]
        plik_z_kodem = sys.argv[2]
        OOFF = False
    elif len(sys.argv) == 4:
        plik_z_programem = sys.argv[1]
        plik_z_kodem = sys.argv[2]
        if sys.argv[3] == "-OOFF" or sys.argv[3] == "-ooff":
            OOFF = True
        else:
            wyrzuc_blad("Błąd: nierozpoznana flaga")
    else:
        wyrzuc_blad("Błąd: niepodano odpowiedniej liczby argumentów")

    # Czytanie programu
    with open(plik_z_programem, "r") as plik:
        program = plik.read()

    # Analiza leksykalna
    lexer = Lexer()

    # Analiza składniowa
    deklaracje, instrukcje = Parser(lexer).parse(program)

    # Analiza semantyczna
    deklaracje, instrukcje = AS(deklaracje, instrukcje).start()
    # Optymalizacja kodu wynikowego
    if not OOFF:
        deklaracje, instrukcje = OPT(deklaracje, instrukcje).start()
    # Stworzenie grafu przepływu sterowania 
    gps = GPS(deklaracje, instrukcje).start()

    # Generacja kodu wynikowego
    kod = GKMW(gps, deklaracje).start()

    # Zapis kodu wynikowego
    with open(plik_z_kodem, "w") as plik:
        plik.write(kod)

    print("Kompilacja zakończona sukcesem! Kod zapisany do pliku: \"" + plik_z_kodem + "\"")

if __name__ == "__main__":
    main()