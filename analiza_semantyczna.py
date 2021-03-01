#!/usr/bin/env python3
# -*- coding: utf-8 -*- 


class AnalizatorSymantyczny(object):
    def __init__(self, deklaracje, instrukcje):
        self.deklaracje = deklaracje
        self.instrukcje = instrukcje
        self.zadeklarowane = []
        self.zainicjowane = []
        self.uzywane_iteratory = []



    def start(self):
        self.sprawdz_deklaracje()
        self.sprawdz_instrukcje(self.instrukcje)
        return self.deklaracje, self.instrukcje

    def wyrzuc_blad(self, tresc):
        print(tresc)
        exit(-1)

    def sprawdz_deklaracje(self):
        sprawdzone_deklaracje = []
        for d in self.deklaracje:
            if d[1] not in self.zadeklarowane:
                self.zadeklarowane.append(d[1])
                # usuwa niepotrzebna juz linie w kodzie
                sprawdzone_deklaracje.append(d[:-1])
            else:
                self.wyrzuc_blad("Błąd: podwójna deklaracja \"" + str(d[1]) + "\" [linia " + str(d[-1]) + "]")

        # zgłasza błąd jeśli podano zły zakres tablicy
        for d in self.deklaracje:
            if d[0] == 'tablica':
                if d[2] > d[3]:
                    self.wyrzuc_blad("Błąd: zły zakres tablicy \"" + str(d[1]) + "\" [linia " + str(d[-1]) + "]")
        self.deklaracje = sprawdzone_deklaracje


    def sprawdz_instrukcje(self, instrukcje):
        for k in instrukcje:
            getattr(self, 'sprawdz_' + k[0])(k)


    def sprawdz_zmienna(self, zmienna):

        if isinstance(zmienna, int):
            return
        if zmienna[1] in self.uzywane_iteratory:
            return

        for zit in self.deklaracje:
            if zit[1] == zmienna[1]:
                if zit[0] != zmienna[0]:
                    self.wyrzuc_blad("Błąd: zły typ \"" + str(zmienna[1]) + "\" [linia " + str(zmienna[-1]) + "]")

        if zmienna[1] not in self.zadeklarowane:
            self.wyrzuc_blad("Błąd: zmnienna \"" + str(zmienna[1]) + "\" niezadeklarowana [linia " + str(zmienna[-1]) + "]")

        if zmienna[0] == 'tablica':
            if isinstance(zmienna[2], int):
                return
            if zmienna[2] in self.uzywane_iteratory:
                return
            if zmienna[2] not in self.zadeklarowane:
                self.wyrzuc_blad("Błąd: zmnienna \"" + str(zmienna[2]) + "\" niezadeklarowana [linia " + str(zmienna[-1]) + "]")
            if zmienna[2] not in self.zainicjowane:
                self.wyrzuc_blad("Błąd: użycie niezainicjowanej zmiennej \"" + str(zmienna[2]) + "\" [linia " + str(zmienna[-1]) + "]")
                
                 
    def sprawdz_wyrazenie(self, instrukcja):
        if len(instrukcja) == 4:
            lewa = instrukcja[2]
            prawa = instrukcja[3]
            self.sprawdz_zmienna(lewa)
            self.sprawdz_zmienna(prawa)
            self.sprawdz_zainicjowanie(lewa)
            self.sprawdz_zainicjowanie(prawa)
        else:
            wartosc = instrukcja[1]
            self.sprawdz_zmienna(wartosc)
            self.sprawdz_zainicjowanie(wartosc)

    def sprawdz_zainicjowanie(self, zmienna):
        if isinstance(zmienna, int):
            return
        if zmienna[1] in self.uzywane_iteratory:
            return

        if zmienna[1] not in self.zainicjowane:
            self.wyrzuc_blad("Błąd: użycie niezainicjowanej zmiennej \"" + str(zmienna[1]) + "\" [linia " + str(zmienna[-1]) + "]")


    def sprawdz_read(self, instrukcja):
        zmienna = instrukcja[1]
        
        self.sprawdz_zmienna(zmienna)
        self.zainicjowane.append(zmienna[1])


    def sprawdz_write(self, instrukcja):
        wartosc = instrukcja[1]
        if isinstance(wartosc, int):
            return

        self.sprawdz_zmienna(wartosc)
        self.sprawdz_zainicjowanie(wartosc)

    
    def sprawdz_while(self, instrukcja):
        warunek = instrukcja[1]
        instrukcje = instrukcja[2]
        self.sprawdz_warunek(warunek)
        self.sprawdz_instrukcje(instrukcje)


    def sprawdz_repeat_until(self, instrukcja):
        instrukcje = instrukcja[1] 
        warunek = instrukcja[2]
        self.sprawdz_warunek(warunek)
        self.sprawdz_instrukcje(instrukcje)


    def sprawdz_warunek(self, instrukcja):
        lewa = instrukcja[2]
        prawa = instrukcja[3]

        self.sprawdz_zmienna(lewa)
        self.sprawdz_zmienna(prawa)
        self.sprawdz_zainicjowanie(lewa)
        self.sprawdz_zainicjowanie(prawa)


    def sprawdz_if_then_else(self, instrukcja):
        warunek = instrukcja[1]
        prawda_instrukcje = instrukcja[2]
        falsz_instrukcje = instrukcja[3]

        self.sprawdz_warunek(warunek)
        self.sprawdz_instrukcje(prawda_instrukcje)
        self.sprawdz_instrukcje(falsz_instrukcje)


    def sprawdz_if_then(self, instrukcja):
        warunek = instrukcja[1]
        instrukcje = instrukcja[2]

        self.sprawdz_warunek(warunek)
        self.sprawdz_instrukcje(instrukcje)


    def sprawdz_przypisz(self, instrukcja):
        identyfikator = instrukcja[1]
        wyrazenie = instrukcja[2]
        self.sprawdz_zmienna(identyfikator)
        self.sprawdz_wyrazenie(wyrazenie)
        self.zainicjowane.append(identyfikator[1])


    def sprawdz_for_to(self, instrukcja):
        iterator = instrukcja[1]
        start = instrukcja[2]
        koniec = instrukcja[3]
        instrukcje = instrukcja[4]
        

        if isinstance(start, int) and isinstance(koniec, int):
            if start > koniec:
                self.wyrzuc_blad("Błąd: niepoprawy zakres pętli FOR TO [Linia ?]")
        
        for i in instrukcje:
            if i[0] == "przypisz":
                if i[1][1] == iterator:
                    self.wyrzuc_blad("Błąd: nie wolno modyfikować iteratora pętli FOR [Linia " + str(i[1][2])+ "]")

        self.sprawdz_zmienna(start)
        self.sprawdz_zmienna(koniec)
        self.uzywane_iteratory.append(iterator)
        self.sprawdz_zainicjowanie(start)
        self.sprawdz_zainicjowanie(koniec)

        self.sprawdz_instrukcje(instrukcje)

        self.uzywane_iteratory.remove(iterator)


    def sprawdz_for_downto(self, instrukcja):
        iterator = instrukcja[1]
        start = instrukcja[2]
        koniec = instrukcja[3]
        instrukcje = instrukcja[4]

        if isinstance(start, int) and isinstance(koniec, int):
            if start < koniec:
                self.wyrzuc_blad("Błąd: niepoprawy zakres pętli FOR DOWNTO [Linia ?]")

        for i in instrukcje:
            if i[0] == "przypisz":
                if i[1][1] == iterator:
                    self.wyrzuc_blad("Błąd: nie wolno modyfikować iteratora pętli FOR [Linia " + str(i[1][2])+ "]")

        self.sprawdz_zmienna(start)
        self.sprawdz_zmienna(koniec)
        self.uzywane_iteratory.append(iterator)
        self.sprawdz_zainicjowanie(start)
        self.sprawdz_zainicjowanie(koniec)
        self.sprawdz_instrukcje(instrukcje)
        self.uzywane_iteratory.remove(iterator)

