#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

class GeneratorKoduMaszynyWirtualnej(object):
    def __init__(self, graf, zmienne_i_tablice):
        self.zmienne_i_tablice = zmienne_i_tablice
        self.graf = graf

        self.krok = 0
        self.pamiec = {}
        self.znaczniki = {}
        self.komorka_pamieci = 0
        self.wygenerowany_kod = []


    def start(self):
        self.wyznacz_miejsce_w_pamieci(self.zmienne_i_tablice)

        for x in self.graf:
            getattr(self, "generuj_" + x[0])(x)

        self.dodaj_rozkaz("HALT")
        
        kod_ze_wstawionymi_znacznikami = self.wstaw_wartosci_znacznikow()
        return kod_ze_wstawionymi_znacznikami

    #===============================================
    #============ Funkcje pomocnicze  ==============
    #===============================================
    def wyznacz_miejsce_w_pamieci(self, zmienne_i_tablice):
        for z in zmienne_i_tablice:
            if isinstance(z, tuple):
                if z[0] == 'zmienna':
                    self.pamiec[z[1]] = self.komorka_pamieci
                    self.komorka_pamieci += 1

        for t in zmienne_i_tablice:
            if isinstance(t, tuple):
                if t[0] == 'tablica':
                    nazwa_tablicy = t[1]
                    poczatek_tablicy = t[2]
                    koniec_tablicy = t[3]
                    self.pamiec[nazwa_tablicy] = self.komorka_pamieci
                    self.komorka_pamieci += koniec_tablicy - poczatek_tablicy + 1


    def wstaw_wartosci_znacznikow(self):
        nowy_kod = ""
        nowy_rozkaz = ""
        krok = 0
        for rozkaz in self.wygenerowany_kod:
            krok += 1
            for znak in rozkaz.split(): #dla każdego znaku
                if znak in self.znaczniki: # jeśli znak jest wskaźnikiem
                    znak = str(self.znaczniki[znak] - krok + 1) #krok do ktorego wskazuje - obecny krok
                nowy_rozkaz += znak + " " 
            nowy_kod += nowy_rozkaz + "\n"
            nowy_rozkaz = ""
            

        return nowy_kod[:-1] #usuniecie ostatniej nowej linii


    def dodaj_rozkaz(self, instrukcja):
        self.wygenerowany_kod.append(instrukcja)
        self.krok += 1

  
    def czy_zmienna_zadeklarowana(self, iden):
        if self.zmienne_i_tablice:
            for id in self.zmienne_i_tablice:
                if id[1] == iden and id[0] == 'zmienna':
                    return True
        return False


    def maks_komorka_pamieci(self):
        maks = -1
        for klucz in self.pamiec.keys():
            if self.pamiec[klucz] > maks:
                for z in self.zmienne_i_tablice:
                    if klucz == z[1]:
                        if z[0] == "zmienna":
                            maks = self.pamiec[klucz]
                        elif z[0] == "tablica":
                            maks = self.pamiec[klucz] + (z[3] - z[2])
        return maks
    

    def tablica_pobierz_kp_i_poczatek(self, arr):
        start = 0
        for t in self.zmienne_i_tablice:
            if t[1] == arr[1]:
                start = t[2]
                break

        return self.pamiec[arr[1]], start

    def wyrzuc_blad(self, tresc):
        print(tresc)
        exit(-1)

    #===============================================
    #====== Funkcje pomocnicze generujace kod ======
    #===============================================
    def przechowaj_zmienna(self, zmienna, rejestr):
        if rejestr == "a":
            self.wyrzuc_blad("[Debug]: Rejestr a zajety podczas przechowywania zmiennej")
        rejestr = str(rejestr)
        kp = self.pamiec[zmienna[1]]
        self.zaladuj_liczbe_do_rejestru(kp, "a")
        self.dodaj_rozkaz("STORE " + rejestr + " a")


    def przechowaj_tablice(self, tablica, rejestr):
        if rejestr == "c" or rejestr == "d":
            self.wyrzuc_blad("[Debug]: Rejestry c,d zajete podczas przechowywania tablicy")
        indeks = tablica[2]
        if isinstance(indeks, int):
            kp_tablicy, poczatek_tablicy = self.tablica_pobierz_kp_i_poczatek(tablica)
            kp = kp_tablicy + indeks - poczatek_tablicy
            self.zaladuj_do_rejestru(kp, "c")
            self.dodaj_rozkaz("STORE " + rejestr +" c")
        elif self.czy_zmienna_zadeklarowana(indeks):
            kp_tablicy, poczatek_tablicy = self.tablica_pobierz_kp_i_poczatek(tablica)
            self.zaladuj_do_rejestru(indeks, "c") #indeks 
            self.zaladuj_do_rejestru(kp_tablicy, "d") #kp_tablicy
            self.dodaj_rozkaz("ADD c d") # indeks + kp_tablicy
            self.zaladuj_do_rejestru(poczatek_tablicy, "d") # poczatek_tablicy
            self.dodaj_rozkaz("SUB c d") # indeks + kp_tablicy - poczatek_tablicy
            self.dodaj_rozkaz("STORE " + rejestr + " c")           
        else: 
            self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")


    def zaladuj_liczbe_do_rejestru(self, liczba, rejestr="a"):
        """
            rejestr: domyślnie a
        """
        rejestr = str(rejestr)
        self.dodaj_rozkaz("RESET "+ rejestr)

        if liczba != 0:
            self.dodaj_rozkaz("INC "+ rejestr)
            liczba = bin(liczba)[3:]
            for digit in liczba:
                self.dodaj_rozkaz("SHL " + rejestr)
                if digit == '1':
                    self.dodaj_rozkaz("INC " + rejestr)


    def zaladuj_do_rejestru(self, wartosc, rejestr):
        if rejestr == "a" or rejestr == "b":
            self.wyrzuc_blad("[Debug]: Rejestry a,b zajete podczas ladowania do rejestru")

        if isinstance(wartosc, int):
            self.zaladuj_liczbe_do_rejestru(wartosc, rejestr)
        elif isinstance(wartosc, tuple):
            if wartosc[0] == "zmienna":
                kp = self.pamiec[wartosc[1]]
                self.zaladuj_liczbe_do_rejestru(kp, "a")
                self.dodaj_rozkaz("LOAD " + rejestr + " a")
            elif wartosc[0] == "tablica":
                indeks = wartosc[2]
                if isinstance(indeks, int):
                    kp_tablicy, poczatek_tablicy = self.tablica_pobierz_kp_i_poczatek(wartosc)
                    kp = kp_tablicy + indeks - poczatek_tablicy
                    self.zaladuj_liczbe_do_rejestru(kp, "a")
                    self.dodaj_rozkaz("LOAD " + rejestr + " a")
                elif self.czy_zmienna_zadeklarowana(indeks):
                    kp = self.pamiec[indeks] 
                    self.zaladuj_liczbe_do_rejestru(kp, "a") # kp_indeksu
                    self.dodaj_rozkaz("LOAD a a") # indeks
                    kp_tablicy, poczatek_tablicy = self.tablica_pobierz_kp_i_poczatek(wartosc)
                    self.zaladuj_liczbe_do_rejestru(kp_tablicy, "b") # kp_tablicy
                    self.dodaj_rozkaz("ADD b a") # indeks + kp_tablicy
                    self.zaladuj_liczbe_do_rejestru(poczatek_tablicy, "a")
                    self.dodaj_rozkaz("SUB b a")  # indeks + kp_tablicy - poczatek
                    self.dodaj_rozkaz("LOAD " + rejestr + " b")
                else:
                    self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")
            else:
                    self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")
        elif self.czy_zmienna_zadeklarowana(wartosc):
            kp = self.pamiec[wartosc]
            self.zaladuj_liczbe_do_rejestru(kp, "a")
            self.dodaj_rozkaz("LOAD " + rejestr + " a")
        else:
            self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")



    #===============================================
    #======== Główne funkcje generujace kod ========
    #===============================================
    def generuj_przypisz(self, instrukcja):
        cel = instrukcja[1]
        wyrazenie = instrukcja[2]

        if len(wyrazenie) == 2:
            self.przypisz_wyrazenie_proste(cel, wyrazenie)
        elif len(wyrazenie) == 4:
            operator = wyrazenie[1]
            x = wyrazenie[2]
            y = wyrazenie[3]
            if operator == "+":
                self.przypisz_dodawanie(cel, x, y)
            elif operator == "-":
                self.przypisz_odejmowanie(cel, x, y)
            elif operator == "*":
                self.przypisz_mnozenie(cel, x, y)
            elif operator == "/":
                self.przypisz_dzielenie(cel, x, y)
            elif operator == "%":
                self.przypisz_modulo(cel, x, y)
            else:
                self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")
        else: 
            self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")
    

    def przypisz_wyrazenie_proste(self, cel, wyrazenie):
        wyrazenie = wyrazenie[1]
        if isinstance(cel, tuple):
            if cel[0] == "tablica":
                indeks = cel[2]
                if isinstance(indeks, int):
                    kp_tablicy, poczatek_tablicy = self.tablica_pobierz_kp_i_poczatek(cel)
                    kp = indeks + kp_tablicy - poczatek_tablicy
                    self.zaladuj_do_rejestru(kp, "c")
                    self.zaladuj_do_rejestru(wyrazenie, "d")
                    self.dodaj_rozkaz("STORE d c")
                elif self.czy_zmienna_zadeklarowana(indeks):
                    kp_tablicy, poczatek_tablicy = self.tablica_pobierz_kp_i_poczatek(cel)
                    self.zaladuj_do_rejestru(indeks, "c") # indeks
                    self.zaladuj_do_rejestru(kp_tablicy, "f") #kp_tablicy
                    self.dodaj_rozkaz("ADD f c") # kp_tablicy + indeks
                    self.zaladuj_do_rejestru(poczatek_tablicy, "c")
                    self.dodaj_rozkaz("SUB f c") # kp_tablicy + indeks - poczatek_tablicy
                    self.zaladuj_do_rejestru(wyrazenie, "d")
                    self.dodaj_rozkaz("STORE d f")
                else:
                    self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")
            elif cel[0] == "zmienna":
                self.zaladuj_do_rejestru(wyrazenie, "c")
                self.przechowaj_zmienna(cel, "c")
            else:
                self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")
        elif isinstance(cel, int):
            self.zaladuj_do_rejestru(wyrazenie, "c")
            self.przechowaj_zmienna(cel, "c")
        else:
            self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")


    def przypisz_dodawanie(self, cel, x, y):
        if isinstance(cel, tuple):
            self.zaladuj_do_rejestru(x, "c")
            self.zaladuj_do_rejestru(y, "e")

            self.dodaj_rozkaz("ADD e c")

            if cel[0] == "zmienna":
                self.przechowaj_zmienna(cel, "e")
            elif cel[0] == 'tablica':
                self.przechowaj_tablice(cel, "e")
            else:
                self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")
        else:
            self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")


    def przypisz_odejmowanie(self, cel, x, y):
        if isinstance(cel, tuple):
            self.zaladuj_do_rejestru(x, "e")
            self.zaladuj_do_rejestru(y, "c")

            self.dodaj_rozkaz("SUB e c")

            if cel[0] == "zmienna":
                self.przechowaj_zmienna(cel, "e")
            elif cel[0] == 'tablica':
                self.przechowaj_tablice(cel, "e")
            else:
                self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")
        else:
            self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")


    def przypisz_mnozenie(self, cel, x, y):
        if isinstance(cel, tuple):
            self.zaladuj_do_rejestru(x, "c")
            self.zaladuj_do_rejestru(x, "f")
            self.zaladuj_do_rejestru(y, "d")
            self.zaladuj_do_rejestru(y, "e")

            self.dodaj_rozkaz("SUB f d")
            self.dodaj_rozkaz("JZERO f 5")
            self.dodaj_rozkaz("RESET d")
            self.dodaj_rozkaz("ADD d c") 
            self.dodaj_rozkaz("RESET c")
            self.dodaj_rozkaz("ADD c e")
            self.dodaj_rozkaz("RESET e")
            self.dodaj_rozkaz("JZERO d 8")
            self.dodaj_rozkaz("JZERO c 7")
            self.dodaj_rozkaz("JODD c 2")
            self.dodaj_rozkaz("JUMP 2")
            self.dodaj_rozkaz("ADD e d")
            self.dodaj_rozkaz("SHR c")
            self.dodaj_rozkaz("SHL d")
            self.dodaj_rozkaz("JUMP -6")
           
            if cel[0] == "zmienna":
                self.przechowaj_zmienna(cel, "e")
            elif cel[0] == 'tablica':
                self.przechowaj_tablice(cel, "e")
            else:
                self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")
        else:
            self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")


    def przypisz_dzielenie(self, cel, x, y):
        if isinstance(cel, tuple):
            self.zaladuj_do_rejestru(x, "c")
            self.zaladuj_do_rejestru(y, "d")

            self.dodaj_rozkaz("JZERO d 27")
            self.dodaj_rozkaz("RESET a")
            self.dodaj_rozkaz("ADD a d")
            self.dodaj_rozkaz("RESET f")
            self.dodaj_rozkaz("ADD f a")
            self.dodaj_rozkaz("SUB f c")
            self.dodaj_rozkaz("JZERO f 2")
            self.dodaj_rozkaz("JUMP 3")
            self.dodaj_rozkaz("SHL a")
            self.dodaj_rozkaz("JUMP -6")
            self.dodaj_rozkaz("RESET f")
            self.dodaj_rozkaz("RESET b")
            self.dodaj_rozkaz("ADD b a")
            self.dodaj_rozkaz("SUB b c")
            self.dodaj_rozkaz("JZERO b 4")
            self.dodaj_rozkaz("SHL f")
            self.dodaj_rozkaz("SHR a")
            self.dodaj_rozkaz("JUMP 5")
            self.dodaj_rozkaz("SHL f")
            self.dodaj_rozkaz("INC f")
            self.dodaj_rozkaz("SUB c a")
            self.dodaj_rozkaz("SHR a")
            self.dodaj_rozkaz("RESET b")
            self.dodaj_rozkaz("ADD b d")
            self.dodaj_rozkaz("SUB b a")
            self.dodaj_rozkaz("JZERO b -14")
            self.dodaj_rozkaz("JUMP 2")
            self.dodaj_rozkaz("RESET f")

            if cel[0] == "zmienna":
                self.przechowaj_zmienna(cel, "f")
            elif cel[0] == 'tablica':
                self.przechowaj_tablice(cel, "f")
            else:
                self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")
        else:
            self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")


    def przypisz_modulo(self, cel, x, y):
        if isinstance(cel, tuple):
            self.zaladuj_do_rejestru(x, "e")
            self.zaladuj_do_rejestru(y, "d")
            
            self.dodaj_rozkaz("JZERO d 27")
            self.dodaj_rozkaz("RESET a")
            self.dodaj_rozkaz("ADD a d")
            self.dodaj_rozkaz("RESET f")
            self.dodaj_rozkaz("ADD f a")
            self.dodaj_rozkaz("SUB f e")
            self.dodaj_rozkaz("JZERO f 2")
            self.dodaj_rozkaz("JUMP 3")
            self.dodaj_rozkaz("SHL a")
            self.dodaj_rozkaz("JUMP -6")
            self.dodaj_rozkaz("RESET f")
            self.dodaj_rozkaz("RESET b")
            self.dodaj_rozkaz("ADD b a")
            self.dodaj_rozkaz("SUB b e")
            self.dodaj_rozkaz("JZERO b 4")
            self.dodaj_rozkaz("SHL f")
            self.dodaj_rozkaz("SHR a")
            self.dodaj_rozkaz("JUMP 5")
            self.dodaj_rozkaz("SHL f")
            self.dodaj_rozkaz("INC f")
            self.dodaj_rozkaz("SUB e a")
            self.dodaj_rozkaz("SHR a")
            self.dodaj_rozkaz("RESET b")
            self.dodaj_rozkaz("ADD b d")
            self.dodaj_rozkaz("SUB b a")
            self.dodaj_rozkaz("JZERO b -14")
            self.dodaj_rozkaz("JUMP 2")
            self.dodaj_rozkaz("RESET e")
            

            if cel[0] == "zmienna":
                self.przechowaj_zmienna(cel, "e")
            elif cel[0] == 'tablica':
                self.przechowaj_tablice(cel, "e")
            else:
                self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")
        else:
            self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")


    def generuj_idz_do(self, instrukcja):
        znacznik = instrukcja[1]
        id_znacznika = znacznik[1]
        self.dodaj_rozkaz("JUMP " + str(id_znacznika))


    def generuj_idz_do_jesli(self, instrukcja):
        warunek = instrukcja[1]
        id_znacznika = instrukcja[2][1]
        operator = warunek[1]
        x = warunek[2]
        y = warunek[3]

        if operator == "=":
            self.rowne(x, y, id_znacznika)
        elif operator == "!=":
            self.nie_rowne(x, y, id_znacznika)
        elif operator == "<":
            self.mniejsze(x, y, id_znacznika)
        elif operator == ">":
            self.wieksze(x, y, id_znacznika)
        elif operator == "<=":
            self.mniejsze_rowne(x, y, id_znacznika)
        elif operator == ">=":
            self.wieksze_rowne(x, y, id_znacznika)


    def rowne(self, x, y, id_znacznika):
        self.zaladuj_do_rejestru(x, "c")
        self.zaladuj_do_rejestru(y, "d")
        self.dodaj_rozkaz("RESET a")
        self.dodaj_rozkaz("ADD a c")
        self.dodaj_rozkaz("RESET b")
        self.dodaj_rozkaz("ADD b d")
        self.dodaj_rozkaz("SUB a d")
        self.dodaj_rozkaz("JZERO a 2")
        self.dodaj_rozkaz("JUMP 3")
        self.dodaj_rozkaz("SUB b c")
        self.dodaj_rozkaz("JZERO b " + id_znacznika)



    def nie_rowne(self, x, y, id_znacznika):
        self.zaladuj_do_rejestru(x, "c")
        self.zaladuj_do_rejestru(y, "d")

        self.dodaj_rozkaz("RESET a")
        self.dodaj_rozkaz("ADD a c")
        self.dodaj_rozkaz("RESET b")
        self.dodaj_rozkaz("ADD b d")
        self.dodaj_rozkaz("SUB a d")
        self.dodaj_rozkaz("JZERO a 2")
        self.dodaj_rozkaz("JUMP " + id_znacznika)
        self.dodaj_rozkaz("SUB b c")
        self.dodaj_rozkaz("JZERO b 2")
        self.dodaj_rozkaz("JUMP " + id_znacznika)


    def wieksze(self, x, y, id_znacznika):    
        self.zaladuj_do_rejestru(x, "c")
        self.zaladuj_do_rejestru(y, "d")
        self.dodaj_rozkaz("SUB c d") 
        self.dodaj_rozkaz("JZERO c 2") 
        self.dodaj_rozkaz("JUMP " + id_znacznika)

    def mniejsze(self, x, y, id_znacznika):   
        self.zaladuj_do_rejestru(x, "c")
        self.zaladuj_do_rejestru(y, "d")
        self.dodaj_rozkaz("SUB d c")
        self.dodaj_rozkaz("JZERO d 2") #jesli y - x = 0 to x > y
        self.dodaj_rozkaz("JUMP " + id_znacznika)

    def wieksze_rowne(self, x, y, id_znacznika):
        self.zaladuj_do_rejestru(x, "c")
        self.zaladuj_do_rejestru(y, "d")
        self.dodaj_rozkaz("SUB d c")
        self.dodaj_rozkaz("JZERO d " + id_znacznika)

    def mniejsze_rowne(self, x, y, id_znacznika):
        self.zaladuj_do_rejestru(x, "c")
        self.zaladuj_do_rejestru(y, "d")
        self.dodaj_rozkaz("SUB c d")
        self.dodaj_rozkaz("JZERO c " + id_znacznika)

    def generuj_read(self, instrukcja):
        wartosc = instrukcja[1]
        if isinstance(wartosc, tuple):
            if wartosc[0] == "zmienna":
                kp = self.pamiec[wartosc[1]]
                self.zaladuj_do_rejestru(kp, "c")
                self.dodaj_rozkaz("GET c")
            elif wartosc[0] == "tablica":
                indeks = wartosc[2]
                if isinstance(indeks, int):
                    kp_tablicy, poczatek_tablicy = self.tablica_pobierz_kp_i_poczatek(wartosc)
                    kp = kp_tablicy + indeks - poczatek_tablicy
                    self.zaladuj_do_rejestru(kp, "c")
                    self.dodaj_rozkaz("GET c")
                elif self.czy_zmienna_zadeklarowana(indeks):
                    kp_tablicy, poczatek_tablicy = self.tablica_pobierz_kp_i_poczatek(wartosc)
                    self.zaladuj_do_rejestru(indeks, "c") #indeks
                    self.zaladuj_do_rejestru(kp_tablicy, "d") #kp_tablicy
                    self.dodaj_rozkaz("ADD c d") #indeks+kp_tablicy
                    self.zaladuj_do_rejestru(poczatek_tablicy, "d")#poczatek_tablicy
                    self.dodaj_rozkaz("SUB c d")#indeks+kp_tablicy-poczatek_tablicy
                    self.dodaj_rozkaz("GET c")
                else:
                    self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")
            else:
                self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")
        else:
            self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")
    

    def generuj_write(self, instrukcja):
        wartosc = instrukcja[1]
        if isinstance(wartosc, tuple):
            if wartosc[0] == "zmienna":
                kp = self.pamiec[wartosc[1]]
                self.zaladuj_do_rejestru(kp, "c")
                self.dodaj_rozkaz("PUT c")

            elif wartosc[0] == "tablica":
                indeks = wartosc[2]
                if isinstance(indeks, int):
                    kp_tablicy, poczatek_tablicy = self.tablica_pobierz_kp_i_poczatek(wartosc)
                    kp = indeks + kp_tablicy - poczatek_tablicy
                    self.zaladuj_do_rejestru(kp, "c")
                    self.dodaj_rozkaz("PUT c")
                elif self.czy_zmienna_zadeklarowana(indeks):
                    kp_tablicy, poczatek_tablicy = self.tablica_pobierz_kp_i_poczatek(wartosc)
                    self.zaladuj_do_rejestru(indeks, "c") #indeks
                    self.zaladuj_do_rejestru(kp_tablicy, "d") # kp_tablicy
                    self.dodaj_rozkaz("ADD c d") # indeks + kp_tablicy
                    self.zaladuj_do_rejestru(poczatek_tablicy, "d") # poczatek_tablicy
                    self.dodaj_rozkaz("SUB c d") # indeks + kp_tablicy - poczatek_tablicy
                    self.dodaj_rozkaz("PUT c")
                else:
                    self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")
            else:
                self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")
        elif isinstance(wartosc, int):
            kp = self.maks_komorka_pamieci() + 1
            self.zaladuj_liczbe_do_rejestru(kp, "b")
            self.zaladuj_liczbe_do_rejestru(wartosc, "a")
            self.dodaj_rozkaz("STORE a b")
            self.dodaj_rozkaz("PUT b")
        else:
            self.wyrzuc_blad("!!! [Błąd kompilatora] !!!")


    def generuj_znacznik(self, instrukcja):
        z = instrukcja[1]
        self.znaczniki[z] = self.krok

