#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

class GrafPrzeplywuSterowania(object):
    def __init__(self, deklaracje, instrukcje):
        self.graf = []
        self.znacznik_licznik = 0
        self.zmienne_i_tablice = deklaracje
        self.instrukcje = instrukcje


    def kolejny_znacznik(self):
        self.znacznik_licznik += 1
        return ('znacznik', '@' + str(self.znacznik_licznik))


    def start(self):
        self.dodaj_do_grafu(self.instrukcje)


        return self.graf


    def dodaj_do_grafu(self, instrukcje):
        for k in instrukcje:
            getattr(self, 'instrukcja_' + k[0])(k)


    def warunek_przeciwny(self, warunek):
        nazwa_instrukcji, operator, lewa, prawa = warunek

        if operator == "=":
            return (nazwa_instrukcji, "!=", lewa, prawa)    
        elif operator == "!=":
            return (nazwa_instrukcji, "=", lewa, prawa)    
        elif operator == "<":
            return (nazwa_instrukcji, ">=", lewa, prawa)    
        elif operator == "<=":
            return (nazwa_instrukcji, ">", lewa, prawa)    
        elif operator == ">":
            return (nazwa_instrukcji, "<=", lewa, prawa)    
        elif operator == ">=":
            return (nazwa_instrukcji, "<", lewa, prawa)    


    def idz_do_jesli(self, warunek, znacznik):
        return ('idz_do_jesli', warunek, znacznik)


    def idz_do(self, znacznik):
        return ('idz_do', znacznik)


    def instrukcja_przypisz(self, instrukcja):
        self.graf.append(instrukcja)


    def instrukcja_if_then(self, instrukcja):
        warunek = instrukcja[1]
        instrukcje = instrukcja[2]

        znacznik_koniec_ifa = self.kolejny_znacznik()
        sprawdz_czy_falsz = self.idz_do_jesli(self.warunek_przeciwny(warunek), znacznik_koniec_ifa)

        self.graf.append(sprawdz_czy_falsz)
        self.dodaj_do_grafu(instrukcje)
        self.graf.append(znacznik_koniec_ifa)


    def instrukcja_if_then_else(self, instrukcja):
        warunek = instrukcja[1]
        prawda_instrukcje = instrukcja[2]
        falsz_instrukcje = instrukcja[3]

        znacznik_koniec_ifa = self.kolejny_znacznik()
        znacznik_falsz = self.kolejny_znacznik()
        sprawdz_czy_falsz = self.idz_do_jesli(self.warunek_przeciwny(warunek), znacznik_falsz)

        self.graf.append(sprawdz_czy_falsz)
        self.dodaj_do_grafu(prawda_instrukcje)
        self.graf.append(self.idz_do(znacznik_koniec_ifa))
        self.graf.append(znacznik_falsz)
        self.dodaj_do_grafu(falsz_instrukcje)
        self.graf.append(znacznik_koniec_ifa)


    def instrukcja_while(self, instrukcja):
        warunek = instrukcja[1]
        instrukcje = instrukcja[2]

        znacznik_start_petli = self.kolejny_znacznik()
        znacznik_koniec_petli = self.kolejny_znacznik()
        koniec_jesli_falsz = self.idz_do_jesli(self.warunek_przeciwny(warunek), znacznik_koniec_petli)

        self.graf.append(znacznik_start_petli)
        self.graf.append(koniec_jesli_falsz)
        self.dodaj_do_grafu(instrukcje)
        self.graf.append(self.idz_do(znacznik_start_petli))
        self.graf.append(znacznik_koniec_petli)


    def instrukcja_repeat_until(self, instrukcja):
        instrukcje = instrukcja[1]
        warunek = instrukcja[2]

        znacznik_start_petli = self.kolejny_znacznik()
        znacznik_koniec_petli = self.kolejny_znacznik()
        koniec_jesli_falsz = self.idz_do_jesli(warunek, znacznik_koniec_petli)

        self.graf.append(znacznik_start_petli)
        self.dodaj_do_grafu(instrukcje)
        self.graf.append(koniec_jesli_falsz)
        self.graf.append(self.idz_do(znacznik_start_petli))
        self.graf.append(znacznik_koniec_petli)


    def instrukcja_for_to(self, instrukcja):
        iterator = instrukcja[1]
        start = instrukcja[2]
        koniec = instrukcja[3]
        instrukcje = instrukcja[4]

        iterator_zmienna = ('zmienna', iterator, instrukcja[5])
        koniec_iteratora_zmienna = ('zmienna', iterator + '_koniec', instrukcja[5])
        przypisz_iterator_zmienna = ('przypisz', iterator_zmienna, ('wyrazenie', start))
        przypisz_koniec_iteratora_zmienna = ('przypisz', koniec_iteratora_zmienna, ('wyrazenie', koniec))
        iterator_zmienna_inc = ('przypisz', iterator_zmienna, ('wyrazenie', '+', iterator_zmienna, 1))
        warunek_konca = ('warunek', '>', iterator_zmienna, koniec_iteratora_zmienna)
        znacznik_start_petli = self.kolejny_znacznik()
        znacznik_koniec_petli = self.kolejny_znacznik()

        self.zmienne_i_tablice.append(iterator_zmienna[:-1])
        self.zmienne_i_tablice.append(koniec_iteratora_zmienna[:-1])
       
        self.instrukcja_przypisz(przypisz_iterator_zmienna)
        self.instrukcja_przypisz(przypisz_koniec_iteratora_zmienna)
        self.graf.append(znacznik_start_petli)
        self.graf.append(self.idz_do_jesli(warunek_konca, znacznik_koniec_petli))
        self.dodaj_do_grafu(instrukcje)
        self.instrukcja_przypisz(iterator_zmienna_inc)
        self.graf.append(self.idz_do(znacznik_start_petli))
        self.graf.append(znacznik_koniec_petli)


    def instrukcja_for_downto(self, instrukcja):
        iterator = instrukcja[1]
        start = instrukcja[2]
        koniec = instrukcja[3]
        instrukcje = instrukcja[4]

        iterator_zmienna = ('zmienna', iterator, instrukcja[5])
        koniec_iteratora_zmienna = ('zmienna', iterator + '_end', instrukcja[5])
        przypisz_iterator_zmienna = ('przypisz', iterator_zmienna, ('wyrazenie', start))
        przypisz_koniec_iteratora_zmienna = ('przypisz', koniec_iteratora_zmienna, ('wyrazenie', koniec))
        iterator_zmienna_dec = ('przypisz', iterator_zmienna, ('wyrazenie', '-', iterator_zmienna, 1))
        warunek_konca = ('warunek', '<', iterator_zmienna, koniec_iteratora_zmienna)
        warunek_zera = ('warunek', '<=', iterator_zmienna, koniec_iteratora_zmienna)
        znacznik_start_petli = self.kolejny_znacznik()
        znacznik_koniec_petli = self.kolejny_znacznik()

        self.zmienne_i_tablice.append(iterator_zmienna)
        self.zmienne_i_tablice.append(koniec_iteratora_zmienna)

        self.instrukcja_przypisz(przypisz_iterator_zmienna)
        self.instrukcja_przypisz(przypisz_koniec_iteratora_zmienna)
        self.graf.append(znacznik_start_petli)
        self.graf.append(self.idz_do_jesli(warunek_konca, znacznik_koniec_petli))
        self.dodaj_do_grafu(instrukcje)
        self.graf.append(self.idz_do_jesli(warunek_zera, znacznik_koniec_petli))
        self.instrukcja_przypisz(iterator_zmienna_dec)
        self.graf.append(self.idz_do(znacznik_start_petli))
        self.graf.append(znacznik_koniec_petli)


    def instrukcja_read(self, instrukcja):
        self.graf.append(instrukcja)


    def instrukcja_write(self, instrukcja):
        self.graf.append(instrukcja)

    