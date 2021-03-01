#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

class Optymalizator(object):
    def __init__(self, deklaracje, instrukcje):
        self.deklaracje = deklaracje
        self.instrukcje = instrukcje
        self.wypisywane = []
        self.powiazania = {}
        self.propagacja = {}
        self.zmienna_w_bloku = {}
        for z in self.deklaracje:
            self.zmienna_w_bloku[z[1]] = False


    def start(self):   
        info = False
        instrukcje = self.wyliczanie_stalych(self.instrukcje)
        instrukcje = self.propagacja_stalych(instrukcje)
        instrukcje = self.wyliczanie_stalych(instrukcje)
        instrukcje = self.usun_glupie(instrukcje)
        if not info and len(instrukcje) > 1000:
            print("Uwaga: optymalizacja może troszkę zająć :)")
            info = True
        self.reset_tablic(instrukcje)
        instrukcje = self.usun_niepowiazane_z_wypisywanymi(instrukcje)
        while instrukcje != self.instrukcje:
            self.instrukcje = instrukcje
            instrukcje = self.wyliczanie_stalych(self.instrukcje)
            self.propagacja = {}
            instrukcje = self.propagacja_stalych(instrukcje)
            instrukcje = self.wyliczanie_stalych(instrukcje)
            instrukcje = self.usun_glupie(instrukcje)
            if not info and len(instrukcje) > 1000:
                print("Uwaga: optymalizacja moze troszke zająć :)")
                info = True
            self.reset_tablic(instrukcje)
            instrukcje = self.usun_niepowiazane_z_wypisywanymi(instrukcje)
        
        self.reset_tablic(instrukcje)
        instrukcje = self.usun_niepowiazane_z_wypisywanymi(instrukcje)
        self.instrukcje = instrukcje

        self.deklaracje = list(dict.fromkeys(self.deklaracje))
        
        return self.deklaracje, self.instrukcje

    def reset_tablic(self, instrukcje):
        self.wypisywane = []
        self.powiazania = {}
        self.zmienna_w_bloku = {}
        for z in self.deklaracje:
            self.zmienna_w_bloku[z[1]] = False
        self.wyznacz_wypisywane(instrukcje)
        self.wyznacz_powiazania(instrukcje)


    def wyznacz_wypisywane(self, instrukcje, iterator = "", linia = -1):
        for instrukcja in instrukcje:
            nazwa_instrukcji = instrukcja[0]
   
            if nazwa_instrukcji == "for_to" or nazwa_instrukcji == "for_downto":
                istrukcje_w_bloku = instrukcja[4]
                self.wyznacz_wypisywane(istrukcje_w_bloku, instrukcja[1], instrukcja[5])
            elif nazwa_instrukcji == "while" or nazwa_instrukcji == "if_then":
                istrukcje_w_bloku = instrukcja[2]
                self.wyznacz_wypisywane(istrukcje_w_bloku)
            elif nazwa_instrukcji == "repeat_until":
                istrukcje_w_bloku = instrukcja[1]
                self.wyznacz_wypisywane(istrukcje_w_bloku)
            elif nazwa_instrukcji == "if_then_else":
                istrukcje_w_bloku_prawdy = instrukcja[2]
                istrukcje_w_bloku_falszu = instrukcja[3]
                self.wyznacz_wypisywane(istrukcje_w_bloku_prawdy)
                self.wyznacz_wypisywane(istrukcje_w_bloku_falszu)
            elif nazwa_instrukcji == "write":
                wypisywana = instrukcja[1]
                if isinstance(wypisywana, tuple):
                    nazwa = wypisywana[1]
                    if nazwa not in self.wypisywane:
                        self.wypisywane.append(nazwa)


    def ruszane_zmienne(self, instrukcje):
        ruszane_zmienne = []
        for instrukcja in instrukcje:
            nazwa_instrukcji = instrukcja[0]

            if nazwa_instrukcji == "przypisz":
                zmienna = instrukcja[1]
                if isinstance(zmienna, tuple):
                    nazwa_zmiennej = zmienna[1] 
                    ruszane_zmienne.append(nazwa_zmiennej)
            elif nazwa_instrukcji == "for_to" or nazwa_instrukcji == "for_downto":
                istrukcje_w_bloku = instrukcja[4]
                nrz = self.ruszane_zmienne(istrukcje_w_bloku)
                ruszane_zmienne.extend(nrz)
            elif nazwa_instrukcji == "while" or nazwa_instrukcji == "if_then":
                istrukcje_w_bloku = instrukcja[2]
                nrz = self.ruszane_zmienne(istrukcje_w_bloku)
                ruszane_zmienne.extend(nrz)
            elif nazwa_instrukcji == "repeat_until":
                istrukcje_w_bloku = instrukcja[1]
                nrz = self.ruszane_zmienne(istrukcje_w_bloku)
                ruszane_zmienne.extend(nrz)
            elif nazwa_instrukcji == "if_then_else":
                istrukcje_w_bloku_prawdy = instrukcja[2]
                istrukcje_w_bloku_falszu = instrukcja[3]
                nrz1 = self.ruszane_zmienne(istrukcje_w_bloku_prawdy)
                nrz2 = self.ruszane_zmienne(istrukcje_w_bloku_falszu)
                ruszane_zmienne.extend(nrz1)
                ruszane_zmienne.extend(nrz2)
            elif nazwa_instrukcji == "write":
                zmienna = instrukcja[1]
                if isinstance(zmienna, tuple):
                    nazwa_zmiennej = zmienna[1] 
                    ruszane_zmienne.append(nazwa_zmiennej)
            elif nazwa_instrukcji == "read":
                zmienna = instrukcja[1]
                if isinstance(zmienna, tuple):
                    nazwa_zmiennej = zmienna[1] 
                    ruszane_zmienne.append(nazwa_zmiennej)
        return list(dict.fromkeys(ruszane_zmienne))


    def wyznacz_powiazania(self, instrukcje, iterator = "", linia = -1):
        if instrukcje == self.instrukcje:
            for wyp in self.wypisywane:
                self.powiazania[wyp] = []
        for instrukcja in instrukcje:
            nazwa_instrukcji = instrukcja[0]
            
            if nazwa_instrukcji == "for_to" or nazwa_instrukcji == "for_downto":
                istrukcje_w_bloku = instrukcja[4]

                ruszane_zmienne = self.ruszane_zmienne(istrukcje_w_bloku)
                
                iterator = instrukcja[1]
                for z in ruszane_zmienne:
                    if z in self.powiazania:
                        if iterator not in self.powiazania[z]:
                            if not isinstance(iterator, int):
                                self.powiazania[z].append(iterator)
                    else:
                        if not isinstance(iterator, int):
                            self.powiazania[z] = [iterator]

                start = instrukcja[2]
                if isinstance(start, tuple):
                    if start[0] == "tablica" and not isinstance(start[2], int):
                        if start[2] in self.powiazania:
                            if start[1] not in self.powiazania[start[2]]:
                                self.powiazania[start[2]].append(start[1])
                        else: 
                            self.powiazania[start[2]] = [start[1]]

                        if start[1] in self.powiazania:
                            if start[2] not in self.powiazania[start[1]]:
                                self.powiazania[start[1]].append(start[2])
                        else: 
                            self.powiazania[start[1]] = [start[2]]
                            
                    start = start[1]
                    for z in ruszane_zmienne:
                        if z in self.powiazania:
                            if start not in self.powiazania[z]:
                                self.powiazania[z].append(start)
                        else:
                            self.powiazania[z] = [start]
                    
                koniec = instrukcja[3]
                if isinstance(koniec, tuple):
                    if koniec[0] == "tablica" and not isinstance(koniec[2], int):
                        if koniec[2] in self.powiazania:
                            if koniec[1] not in self.powiazania[koniec[2]]:
                                self.powiazania[koniec[2]].append(koniec[1])
                        else: 
                            self.powiazania[koniec[2]] = [koniec[1]]

                        if koniec[1] in self.powiazania:
                            if koniec[2] not in self.powiazania[koniec[1]]:
                                self.powiazania[koniec[1]].append(koniec[2])
                        else: 
                            self.powiazania[koniec[1]] = [koniec[2]]
                    koniec = koniec[1]
                    for z in ruszane_zmienne:
                        if z in self.powiazania:
                            if koniec not in self.powiazania[z]:
                                self.powiazania[z].append(koniec)
                        else:
                            self.powiazania[z] = [koniec]

                

                self.wyznacz_powiazania(istrukcje_w_bloku, instrukcja[1], instrukcja[5])
            elif nazwa_instrukcji == "while" or nazwa_instrukcji == "if_then":
                warunek = instrukcja[1]
                istrukcje_w_bloku = instrukcja[2]
                x = warunek[2]
                ruszane_zmienne = self.ruszane_zmienne(istrukcje_w_bloku)
                if isinstance(x, tuple):
                    if x[0] == "tablica" and not isinstance(x[2], int):
                        if x[2] in self.powiazania:
                            if x[1] not in self.powiazania[x[2]]:
                                self.powiazania[x[2]].append(x[1])
                        else: 
                            self.powiazania[x[2]] = [x[1]]

                        if x[1] in self.powiazania:
                            if x[2] not in self.powiazania[x[1]]:
                                self.powiazania[x[1]].append(x[2])
                        else: 
                            self.powiazania[x[1]] = [x[2]]
                    x = x[1]
                
                    for z in ruszane_zmienne:
                        if z in self.powiazania:
                            if x not in self.powiazania[z]:
                                self.powiazania[z].append(x)
                        else:
                            self.powiazania[z] = [x]
                y = warunek[3]
                if isinstance(y, tuple):
                    if y[0] == "tablica" and not isinstance(y[2], int):
                        if y[2] in self.powiazania:
                            if y[1] not in self.powiazania[y[2]]:
                                self.powiazania[y[2]].append(y[1])
                        else: 
                            self.powiazania[y[2]] = [y[1]]

                        if y[1] in self.powiazania:
                            if y[2] not in self.powiazania[y[1]]:
                                self.powiazania[y[1]].append(y[2])
                        else: 
                            self.powiazania[y[1]] = [y[2]]
                    y = y[1]
 
                    for z in ruszane_zmienne:
                        if z in self.powiazania:
                            if y not in self.powiazania[z]:
                                self.powiazania[z].append(y)
                        else:
                            self.powiazania[z] = [y]            
                self.wyznacz_powiazania(istrukcje_w_bloku)
            elif nazwa_instrukcji == "repeat_until":
                istrukcje_w_bloku = instrukcja[1]
                warunek = instrukcja[2]
                x = warunek[2]
                ruszane_zmienne = self.ruszane_zmienne(istrukcje_w_bloku)
                if isinstance(x, tuple):
                    if x[0] == "tablica"  and not isinstance(x[2], int):
                        if x[2] in self.powiazania:
                            if x[1] not in self.powiazania[x[2]]:
                                self.powiazania[x[2]].append(x[1])
                        else: 
                            self.powiazania[x[2]] = [x[1]]

                        if x[1] in self.powiazania:
                            if x[2] not in self.powiazania[x[1]]:
                                self.powiazania[x[1]].append(x[2])
                        else: 
                            self.powiazania[x[1]] = [x[2]]
                    x = x[1]
   
        
                    for z in ruszane_zmienne:
                        if z in self.powiazania:
                            if x not in self.powiazania[z]:
                                self.powiazania[z].append(x)
                        else:
                            self.powiazania[z] = [x]
                y = warunek[3]
                if isinstance(y, tuple):
                    if y[0] == "tablica"  and not isinstance(y[2], int):
                        if y[1] not in self.powiazania[y[2]]:
                            self.powiazania[y[2]].append(y[1])
                        else: 
                            self.powiazania[y[2]] = [y[1]]

                        if y[1] in self.powiazania:
                            if y[2] not in self.powiazania[y[1]]:
                                self.powiazania[y[1]].append(y[2])
                        else: 
                            self.powiazania[y[1]] = [y[2]]
                    y = y[1]

                    for z in ruszane_zmienne:
                        if z in self.powiazania:
                            if y not in self.powiazania[z]:
                                self.powiazania[z].append(y)
                        else:
                            self.powiazania[z] = [y]          
                self.wyznacz_powiazania(istrukcje_w_bloku)
            elif nazwa_instrukcji == "if_then_else":
                istrukcje_w_bloku_prawdy = instrukcja[2]
                istrukcje_w_bloku_falszu = instrukcja[3]
                warunek = instrukcja[1]

                x = warunek[2]
                ruszane_zmienne1 = self.ruszane_zmienne(istrukcje_w_bloku_prawdy)
                ruszane_zmienne2 = self.ruszane_zmienne(istrukcje_w_bloku_falszu)
                ruszane_zmienne1.extend(ruszane_zmienne2)
                ruszane_zmienne = list(dict.fromkeys(ruszane_zmienne1))
                if isinstance(x, tuple):
                    if x[0] == "tablica" and not isinstance(x[2], int):
                        if x[2] in self.powiazania:
                            if x[1] not in self.powiazania[x[2]]:
                                self.powiazania[x[2]].append(x[1])
                        else: 
                            self.powiazania[x[2]] = [x[1]]

                        if x[1] in self.powiazania:
                            if x[2] not in self.powiazania[x[1]]:
                                self.powiazania[x[1]].append(x[2])
                        else: 
                            self.powiazania[x[1]] = [x[2]]

                    x = x[1]
                    for z in ruszane_zmienne:
                        if z in self.powiazania:
                            if x not in self.powiazania[z]:
                                self.powiazania[z].append(x)
                        else:
                            self.powiazania[z] = [x]
       
                y = warunek[3]
                if isinstance(y, tuple):
                    if y[0] == "tablica":
                        if y[2] in self.powiazania:
                            if y[1] not in self.powiazania[y[2]]:
                                self.powiazania[y[2]].append(y[1])
                        else: 
                            self.powiazania[y[2]] = [y[1]]

                        if y[1] in self.powiazania:
                            if y[2] not in self.powiazania[y[1]]:
                                self.powiazania[y[1]].append(y[2])
                        else: 
                            self.powiazania[y[1]] = [y[2]]

                    y = y[1]
           
                    for z in ruszane_zmienne:
                        if z in self.powiazania:
                            if y not in self.powiazania[z]:
                                self.powiazania[z].append(y)
                        else:
                            self.powiazania[z] = [y]

                self.wyznacz_powiazania(istrukcje_w_bloku_prawdy)
                self.wyznacz_powiazania(istrukcje_w_bloku_falszu)
            elif nazwa_instrukcji == "przypisz":
                zmienna = instrukcja[1]
                wyrazenie = instrukcja[2]
                
                if isinstance(zmienna, tuple):
                    nazwa_zmiennej = zmienna[1]

                    if not nazwa_zmiennej in self.powiazania:
                        self.powiazania[nazwa_zmiennej] = []

                    if zmienna[0] == "tablica":
                        if not isinstance(zmienna[2], int):
                            if zmienna[2] in self.powiazania:
                                if nazwa_zmiennej not in self.powiazania[zmienna[2]]:
                                    self.powiazania[zmienna[2]].append(nazwa_zmiennej)
                            else: 
                                self.powiazania[zmienna[2]] = [nazwa_zmiennej]

                            if nazwa_zmiennej in self.powiazania:
                                if zmienna[2] not in self.powiazania[nazwa_zmiennej]:
                                    self.powiazania[nazwa_zmiennej].append(zmienna[2])
                            else: 
                                self.powiazania[nazwa_zmiennej] = [zmienna[2]]

                    if len(wyrazenie) == 4:
                        x = wyrazenie[2]
                        if isinstance(x, tuple):
                            nazwa_x = x[1]
                            if x[0] == "tablica":
                                if not isinstance(x[2], int):
                                    if x[2] in self.powiazania:
                                        if x[2] not in self.powiazania[nazwa_zmiennej]:
                                            self.powiazania[nazwa_zmiennej].append(x[2])
                                    else: 
                                        self.powiazania[nazwa_zmiennej] = [x[2]]

                            if nazwa_zmiennej in self.powiazania:
                                if nazwa_x not in self.powiazania[nazwa_zmiennej]:
                                    self.powiazania[nazwa_zmiennej].append(nazwa_x)
                            else: 
                                self.powiazania[nazwa_zmiennej] = [nazwa_x]

                        y = wyrazenie[3]
                        if isinstance(y, tuple):
                            nazwa_y = y[1]
                            if y[0] == "tablica":
                                if not isinstance(y[2], int):
                                    if y[2] in self.powiazania:
                                        if y[2] not in self.powiazania[nazwa_zmiennej]:
                                            self.powiazania[nazwa_zmiennej].append(y[2])
                                    else: 
                                        self.powiazania[nazwa_zmiennej] = [y[2]]

                            if nazwa_zmiennej in self.powiazania:
                                if nazwa_y not in self.powiazania[nazwa_zmiennej]:
                                    self.powiazania[nazwa_zmiennej].append(nazwa_y)
                            else:
                                self.powiazania[nazwa_zmiennej] = [nazwa_y]
                
                    else:
                        x = wyrazenie[1]
                        if isinstance(x, tuple):
                            nazwa_x = x[1]
                            if nazwa_zmiennej in self.powiazania:
                                if nazwa_x not in self.powiazania[nazwa_zmiennej]:
                                    self.powiazania[nazwa_zmiennej].append(nazwa_x)
                            else:
                                self.powiazania[nazwa_zmiennej] = [nazwa_x]

            elif nazwa_instrukcji == "write":
                wypisywana = instrukcja[1]
                if isinstance(wypisywana, tuple):
                    if wypisywana[0] == "tablica":
                        if not isinstance(wypisywana[2], int):
                            if wypisywana[2] in self.powiazania:
                                if wypisywana[1] not in self.powiazania[wypisywana[2]]:
                                    self.powiazania[wypisywana[2]].append(wypisywana[1])
                            else: 
                                self.powiazania[wypisywana[2]] = [wypisywana[1]]

                            if wypisywana[1] in self.powiazania:
                                if wypisywana[2] not in self.powiazania[wypisywana[1]]:
                                    self.powiazania[wypisywana[1]].append(wypisywana[2])
                            else: 
                                self.powiazania[wypisywana[1]] = [wypisywana[2]]

            elif nazwa_instrukcji == "read":
                czytana = instrukcja[1]
                if isinstance(czytana, tuple):
                    if czytana[0] == "tablica":
                        if czytana[2] in self.powiazania:
                            if czytana[1] not in self.powiazania[czytana[2]]:
                                self.powiazania[czytana[2]].append(czytana[1])
                        else: 
                            self.powiazania[czytana[2]] = [czytana[1]]

                        if czytana[1] in self.powiazania:
                            if czytana[2] not in self.powiazania[czytana[1]]:
                                self.powiazania[czytana[1]].append(czytana[2])
                        else: 
                            self.powiazania[czytana[1]] = [czytana[2]]

       

        for glowna in self.powiazania:
            if not isinstance(glowna, int): #skad sie biora te indeksy?
                self.powiazania[glowna] = list(dict.fromkeys(self.powiazania[glowna])) # a skad powtorzenia?
                for powiazana in self.powiazania[glowna]:
                    if powiazana == glowna:
                        continue
                    if powiazana in self.powiazania:
                        for x in self.powiazania[powiazana]:
                            if x == glowna:
                                continue
                            if not x in self.powiazania[glowna]:
                                self.powiazania[glowna].append(x)


    def czy_jest_write(self, instrukcje):
        for instrukcja in instrukcje:
            nazwa_instrukcji = instrukcja[0]

            if nazwa_instrukcji == "for_to" or nazwa_instrukcji == "for_downto":
                istrukcje_w_bloku = instrukcja[4]
                x = self.czy_jest_write(istrukcje_w_bloku)
                if x:
                    return True
            elif nazwa_instrukcji == "while" or nazwa_instrukcji == "if_then":
                istrukcje_w_bloku = instrukcja[2]
                x = self.czy_jest_write(istrukcje_w_bloku)
                if x:
                    return True
            elif nazwa_instrukcji == "repeat_until":
                istrukcje_w_bloku = instrukcja[1]
                x = self.czy_jest_write(istrukcje_w_bloku)
                if x:
                    return True
            elif nazwa_instrukcji == "if_then_else":
                istrukcje_w_bloku_prawdy = instrukcja[2]
                istrukcje_w_bloku_falszu = instrukcja[3]
                x = self.czy_jest_write(istrukcje_w_bloku_prawdy)
                if x:
                    return True
                x = self.czy_jest_write(istrukcje_w_bloku_falszu)
                if x:
                    return True
            elif nazwa_instrukcji == "write":
                return True
        return False


    def usun_niepowiazane_z_wypisywanymi(self, instrukcje, iterator = "", linia = -1):
        nowe_istrukcje = []
        for instrukcja in instrukcje:
            nazwa_instrukcji = instrukcja[0]
   
            if nazwa_instrukcji == "for_to" or nazwa_instrukcji == "for_downto":
                istrukcje_w_bloku = instrukcja[4]
                niwb = self.usun_niepowiazane_z_wypisywanymi(istrukcje_w_bloku, instrukcja[1], instrukcja[5])
                czy_write = self.czy_jest_write(niwb)
                if czy_write:
                    nowe_istrukcje.append(instrukcja)
                elif niwb:
                    dodaj = (nazwa_instrukcji, instrukcja[1], instrukcja[2], instrukcja[3], niwb, instrukcja[5])
                    nowe_istrukcje.append(dodaj)
            elif nazwa_instrukcji == "while" or nazwa_instrukcji == "if_then":
                istrukcje_w_bloku = instrukcja[2]
                niwb = self.usun_niepowiazane_z_wypisywanymi(istrukcje_w_bloku)
                czy_write = self.czy_jest_write(niwb)
                if czy_write:
                    nowe_istrukcje.append(instrukcja)
                elif niwb:
                    dodaj = (nazwa_instrukcji, instrukcja[1], niwb)
                    nowe_istrukcje.append(dodaj)
            elif nazwa_instrukcji == "repeat_until":
                istrukcje_w_bloku = instrukcja[1]
                niwb = self.usun_niepowiazane_z_wypisywanymi(istrukcje_w_bloku)
                czy_write = self.czy_jest_write(niwb)
                if czy_write:
                    nowe_istrukcje.append(instrukcja)
                elif niwb:
                    dodaj = (nazwa_instrukcji, niwb, instrukcja[2])
                    nowe_istrukcje.append(dodaj)
            elif nazwa_instrukcji == "if_then_else":
                istrukcje_w_bloku_prawdy = instrukcja[2]
                istrukcje_w_bloku_falszu = instrukcja[3]
                niwbp = self.usun_niepowiazane_z_wypisywanymi(istrukcje_w_bloku_prawdy)
                niwbf = self.usun_niepowiazane_z_wypisywanymi(istrukcje_w_bloku_falszu)
                czy_write1 = self.czy_jest_write(niwbp)
                czy_write2 = self.czy_jest_write(niwbf)
                if czy_write1 or czy_write2:
                    nowe_istrukcje.append(instrukcja)
                elif niwbp and niwbf:
                    dodaj = (nazwa_instrukcji, instrukcja[1], niwbp, niwbf)
                    nowe_istrukcje.append(dodaj)
                elif niwbp:
                    dodaj = ("if_then", instrukcja[1], niwbp)
                    nowe_istrukcje.append(dodaj)
                elif niwbf:
                    warunek = instrukcja[1]
                    operator = warunek[1]
                    if operator == "=":
                        operator = "!="
                    elif operator == "!=":
                        operator = "="
                    elif operator == "<":
                        operator = ">="  
                    elif operator == "<=":
                        operator = ">"   
                    elif operator == ">":
                        operator = "<="   
                    elif operator == ">=":
                        operator = "<"
                    warunek = (warunek[0], operator, warunek[2], warunek[3])
                    dodaj = ("if_then", warunek, niwbf)
                    nowe_istrukcje.append(dodaj)

            elif nazwa_instrukcji == "przypisz":
                zmienna = instrukcja[1]
                wypisac = False
                if isinstance(zmienna, tuple):
                    nazwa_zmiennej = zmienna[1]
        
                if nazwa_zmiennej in self.wypisywane:
                    wypisac = True
                
                for glowna in self.powiazania:
                    if glowna in self.wypisywane:
                        if nazwa_zmiennej in self.powiazania[glowna]:
                            wypisac = True
                            break
                
                if wypisac:
                    nowe_istrukcje.append(instrukcja)
                
            else:
                nowe_istrukcje.append(instrukcja)



                    

        return nowe_istrukcje
    

    def wyliczanie_stalych(self, instrukcje):
        nowe_istrukcje = []
        for instrukcja in instrukcje:
            nazwa_instrukcji = instrukcja[0]
   
            if nazwa_instrukcji == "for_to" or nazwa_instrukcji == "for_downto":
                istrukcje_w_bloku = instrukcja[4]
                nowe_istrukcje_w_bloku = self.wyliczanie_stalych(istrukcje_w_bloku)
                dodaj = (nazwa_instrukcji, instrukcja[1], instrukcja[2], instrukcja[3], nowe_istrukcje_w_bloku, instrukcja[5])
                nowe_istrukcje.append(dodaj)
            elif nazwa_instrukcji == "while" or nazwa_instrukcji == "if_then":
                istrukcje_w_bloku = instrukcja[2]
                nowe_istrukcje_w_bloku = self.wyliczanie_stalych(istrukcje_w_bloku)
                dodaj = (nazwa_instrukcji, instrukcja[1], nowe_istrukcje_w_bloku)
                nowe_istrukcje.append(dodaj)
            elif nazwa_instrukcji == "repeat_until":
                istrukcje_w_bloku = instrukcja[1]
                nowe_istrukcje_w_bloku = self.wyliczanie_stalych(istrukcje_w_bloku)
                dodaj = (nazwa_instrukcji, nowe_istrukcje_w_bloku, instrukcja[2])
                nowe_istrukcje.append(dodaj)
            elif nazwa_instrukcji == "if_then_else":
                istrukcje_w_bloku_prawdy = instrukcja[2]
                istrukcje_w_bloku_falszu = instrukcja[3]
                nowe_istrukcje_w_bloku_prawdy = self.wyliczanie_stalych(istrukcje_w_bloku_prawdy)
                nowe_istrukcje_w_bloku_falszu = self.wyliczanie_stalych(istrukcje_w_bloku_falszu)
                dodaj = (nazwa_instrukcji,  instrukcja[1], nowe_istrukcje_w_bloku_prawdy, nowe_istrukcje_w_bloku_falszu)
                nowe_istrukcje.append(dodaj)
            elif nazwa_instrukcji == "przypisz":
                zmienna = instrukcja[1]
                wyrazenie = instrukcja[2]

                if len(wyrazenie) == 4:
                    operator = wyrazenie[1]
                    x = wyrazenie[2]
                    y = wyrazenie[3]
                    if isinstance(x, int) and isinstance(y, int):
                        if operator == "+":
                            wyrazenie = ("wyrazenie", x+y)
                        elif operator == "-":
                            wyrazenie = ("wyrazenie", x-y)
                        elif operator == "*":
                            wyrazenie = ("wyrazenie", x*y)
                        elif operator == "/":
                            if y == 0:
                                wyrazenie = ("wyrazenie", 0)
                            else:
                                wyrazenie = ("wyrazenie", x//y)
                        elif operator == "%":
                            if y == 0:
                                wyrazenie = ("wyrazenie", 0)
                            else:
                                wyrazenie = ("wyrazenie", x%y)

                    elif isinstance(x, int) and not isinstance(y, int):
                        if operator == "+" and x == 0:
                            wyrazenie = ("wyrazenie", y)
                        elif operator == "-" and x == 0:
                            wyrazenie = ("wyrazenie", 0)
                        elif operator == "*" and x == 1:
                            wyrazenie = ("wyrazenie", y)
                        elif operator == "*" and x == 0:
                            wyrazenie = ("wyrazenie", 0)
                        elif operator == "/" and x == 0:
                            wyrazenie = ("wyrazenie", 0)
                        elif operator == "%" and x == 0:
                            wyrazenie = ("wyrazenie", 0)

                    elif not isinstance(x, int) and isinstance(y, int):
                        if operator == "+" and y == 0:
                            wyrazenie = ("wyrazenie", x)
                        elif operator == "-" and y == 0:
                            wyrazenie = ("wyrazenie", x)
                        elif operator == "*" and y == 1:
                            wyrazenie = ("wyrazenie", x)
                        elif operator == "*" and y == 0:
                            wyrazenie = ("wyrazenie", 0)
                        elif operator == "/" and y == 0:
                            wyrazenie = ("wyrazenie", 0)
                        elif operator == "/" and y == 1:
                            wyrazenie = ("wyrazenie", x)
                        elif operator == "%" and y == 0:
                            wyrazenie = ("wyrazenie", 0)
                    elif not isinstance(x, int) and not isinstance(y, int):
                        if x[0] == "zmienna" and y[0] == "zmienna":
                            if operator == "-" and x[1] == y[1]:
                                wyrazenie = ("wyrazenie", 0)
                            elif operator == "/" and x[1] == y[1]:
                                wyrazenie = ("wyrazenie", 1)
                            elif operator == "%" and x[1] == y[1]:
                                wyrazenie = ("wyrazenie", 0)
                        

                dodaj = (nazwa_instrukcji, zmienna, wyrazenie)             
                nowe_istrukcje.append(dodaj)
            else:
                nowe_istrukcje.append(instrukcja)
        return nowe_istrukcje
    

    def propagacja_stalych(self, instrukcje):
        nowe_istrukcje = []
        for instrukcja in instrukcje:
            nazwa_instrukcji = instrukcja[0]

            if nazwa_instrukcji == "for_to" or nazwa_instrukcji == "for_downto":
                start = instrukcja[2]
                # zakres petli nie podlega zmianie nawet jesli 
                # ulegna zmianie zmienne go wyznaczajce 
                if isinstance(start , tuple):
                    if start[0] == "zmienna":
                        if start[1] in self.propagacja and not self.zmienna_w_bloku[start[1]]:
                            start = self.propagacja[start[1]]
                    else:
                        if start[2] in self.propagacja and not self.zmienna_w_bloku[start[2]]:
                            start = (start[0], start[1], self.propagacja[start[2]], start[3])
                
                koniec = instrukcja[3]
                if isinstance(koniec , tuple):
                    if koniec[0] == "zmienna":
                        if koniec[1] in self.propagacja and not self.zmienna_w_bloku[koniec[1]]:
                            koniec = self.propagacja[koniec[1]]
                    else:
                        if koniec[2] in self.propagacja and not self.zmienna_w_bloku[koniec[2]]:
                            koniec = (koniec[0], koniec[1], self.propagacja[koniec[2]], koniec[3])

                for z in self.ruszane_zmienne(instrukcja[4]):
                    self.zmienna_w_bloku[z] = True
                dodaj = (nazwa_instrukcji, instrukcja[1], start, koniec, instrukcja[4], instrukcja[5])
                nowe_istrukcje.append(dodaj)
            elif nazwa_instrukcji == "while":
                for z in self.ruszane_zmienne(instrukcja[2]):
                    self.zmienna_w_bloku[z] = True  
                warunek = instrukcja[1]
                x = warunek[2]
                if isinstance(x , tuple):
                    if x[0] == "zmienna":
                        if x[1] in self.propagacja and not self.zmienna_w_bloku[x[1]]:
                            x = self.propagacja[x[1]]
                    else:
                        if x[2] in self.propagacja and not self.zmienna_w_bloku[x[2]]:
                            x = (x[0], x[1], self.propagacja[x[2]], x[3])
                y = warunek[3]
                if isinstance(y , tuple):
                    if y[0] == "zmienna":
                        if y[1] in self.propagacja and not self.zmienna_w_bloku[y[1]]:
                            y = self.propagacja[y[1]]
                    else:
                        if y[2] in self.propagacja and not self.zmienna_w_bloku[y[2]]:
                            y = (y[0], y[1], self.propagacja[y[2]], y[3]) 

                warunek = (warunek[0], warunek[1], x, y) 
                dodaj = (nazwa_instrukcji, warunek, instrukcja[2])
                nowe_istrukcje.append(dodaj)
            elif nazwa_instrukcji == "if_then":
                warunek = instrukcja[1]
                x = warunek[2]
                if isinstance(x , tuple):
                    if x[0] == "zmienna":
                        if x[1] in self.propagacja and not self.zmienna_w_bloku[x[1]]:
                            x = self.propagacja[x[1]]
                    else:
                        if x[2] in self.propagacja and not self.zmienna_w_bloku[x[2]]:
                            x = (x[0], x[1], self.propagacja[x[2]], x[3])
                y = warunek[3]
                if isinstance(y , tuple):
                    if y[0] == "zmienna":
                        if y[1] in self.propagacja and not self.zmienna_w_bloku[y[1]]:
                            y = self.propagacja[y[1]]
                    else:
                        if y[2] in self.propagacja and not self.zmienna_w_bloku[y[2]]:
                            y = (y[0], y[1], self.propagacja[y[2]], y[3]) 

                for z in self.ruszane_zmienne(instrukcja[2]):
                    self.zmienna_w_bloku[z] = True 
                warunek = (warunek[0], warunek[1], x, y) 
                dodaj = (nazwa_instrukcji, warunek, instrukcja[2])
                nowe_istrukcje.append(dodaj)
            elif nazwa_instrukcji == "repeat_until":
                for z in self.ruszane_zmienne(instrukcja[1]):
                    self.zmienna_w_bloku[z] = True  

                warunek = instrukcja[2]
                x = warunek[2]
                if isinstance(x , tuple):
                    if x[0] == "zmienna":
                        if x[1] in self.propagacja and not self.zmienna_w_bloku[x[1]]:
                            x = self.propagacja[x[1]]
                    else:
                        if x[2] in self.propagacja and not self.zmienna_w_bloku[x[2]]:
                            x = (x[0], x[1], self.propagacja[x[2]], x[3])
                y = warunek[3]
                if isinstance(y , tuple):
                    if y[0] == "zmienna":
                        if y[1] in self.propagacja and not self.zmienna_w_bloku[y[1]]:
                            y = self.propagacja[y[1]]
                    else:
                        if y[2] in self.propagacja and not self.zmienna_w_bloku[y[2]]:
                            y = (y[0], y[1], self.propagacja[y[2]], y[3]) 

                warunek = (warunek[0], warunek[1], x, y) 
                dodaj = (nazwa_instrukcji, instrukcja[1], warunek)
                nowe_istrukcje.append(dodaj)
            elif nazwa_instrukcji == "if_then_else":
                warunek = instrukcja[1]
                x = warunek[2]
                if isinstance(x , tuple):
                    if x[0] == "zmienna":
                        if x[1] in self.propagacja and not self.zmienna_w_bloku[x[1]]:
                            x = self.propagacja[x[1]]
                    else:
                        if x[2] in self.propagacja and not self.zmienna_w_bloku[x[2]]:
                            x = (x[0], x[1], self.propagacja[x[2]], x[3])
                y = warunek[3]

                if isinstance(y , tuple):
                    if y[0] == "zmienna":
                        if y[1] in self.propagacja and not self.zmienna_w_bloku[y[1]]:
                            y = self.propagacja[y[1]]
                    else:
                        if y[2] in self.propagacja and not self.zmienna_w_bloku[y[2]]:
                            y = (y[0], y[1], self.propagacja[y[2]], y[3]) 


                for z in self.ruszane_zmienne(instrukcja[2]):
                    self.zmienna_w_bloku[z] = True
                for z in self.ruszane_zmienne(instrukcja[3]):
                    self.zmienna_w_bloku[z] = True 

                warunek = (warunek[0], warunek[1], x, y) 
                dodaj = (nazwa_instrukcji, warunek, instrukcja[2], instrukcja[3])
                nowe_istrukcje.append(dodaj)                
            elif nazwa_instrukcji == "przypisz":
                zmienna = instrukcja[1]
                wyrazenie = instrukcja[2]
                nazwa_zmiennej = zmienna[1]

                if isinstance(zmienna, tuple):
                    if zmienna[0] == "tablica":
                        if zmienna[2] in self.propagacja and not self.zmienna_w_bloku[zmienna[2]]:
                            zmienna = (zmienna[0], zmienna[1], self.propagacja[zmienna[2]], zmienna[3]) 

                if len(wyrazenie) == 4:
                    operator = wyrazenie[1]
                    x = wyrazenie[2]
                    y = wyrazenie[3]

                    if isinstance(x , tuple):
                        if x[0] == "zmienna":
                            if x[1] in self.propagacja and not self.zmienna_w_bloku[x[1]]:
                                x = self.propagacja[x[1]]
                        else:
                            if x[2] in self.propagacja and not self.zmienna_w_bloku[x[2]]:
                                x = (x[0], x[1], self.propagacja[x[2]], x[3])

                    if isinstance(y , tuple):
                        if y[0] == "zmienna":
                            if y[1] in self.propagacja and not self.zmienna_w_bloku[y[1]]:
                                y = self.propagacja[y[1]]
                        else:
                            if y[2] in self.propagacja and not self.zmienna_w_bloku[y[2]]:
                                y = (y[0], y[1], self.propagacja[y[2]], y[3]) 

                    if isinstance(x, int) and isinstance(y, int):
                        if operator == "+":
                            self.propagacja[nazwa_zmiennej] = x + y
                        elif operator == "-":
                            self.propagacja[nazwa_zmiennej] = x - y
                        elif operator == "*":
                            self.propagacja[nazwa_zmiennej] = x * y
                        elif operator == "/":
                            if y == 0:
                                self.propagacja[nazwa_zmiennej] = 0
                            else:
                                self.propagacja[nazwa_zmiennej] = x // y
                        elif operator == "%":
                            if y == 0:
                                self.propagacja[nazwa_zmiennej] = 0
                            else:
                                self.propagacja[nazwa_zmiennej] = x % y
                    else:
                        if nazwa_zmiennej in self.propagacja:
                            del self.propagacja[nazwa_zmiennej]
                    

                    wyrazenie = ("wyrazenie", operator, x, y)
                else:
                    
                    x = wyrazenie[1]
                    if isinstance(x, int):
                        if zmienna[0] == "zmienna":
                            self.propagacja[nazwa_zmiennej] = x
                            self.zmienna_w_bloku[nazwa_zmiennej] = False
                       
                    if isinstance(x , tuple):
                        if x[0] == "zmienna":
                            if x[1] in self.propagacja and not self.zmienna_w_bloku[x[1]]:
                                x = self.propagacja[x[1]]
                                self.propagacja[nazwa_zmiennej] = x
                            else:
                                if nazwa_zmiennej in self.propagacja:
                                    del self.propagacja[nazwa_zmiennej]
                                
                        

                dodaj = (nazwa_instrukcji, zmienna, wyrazenie)             
                nowe_istrukcje.append(dodaj)

            elif nazwa_instrukcji == "write":
                wypisywana = instrukcja[1]
                if isinstance(wypisywana, tuple):
                    if wypisywana[0] == "zmienna":
                        if wypisywana[1] in self.propagacja and not self.zmienna_w_bloku[wypisywana[1]]:
                            wypisywana = self.propagacja[wypisywana[1]]
                    else:
                        if wypisywana[2] in self.propagacja and not self.zmienna_w_bloku[wypisywana[2]]:
                            wypisywana = (wypisywana[0], wypisywana[1], self.propagacja[wypisywana[2]], wypisywana[3]) 
                
                dodaj = ("write", wypisywana)
                nowe_istrukcje.append(dodaj)
            elif nazwa_instrukcji == "read":
                czytana = instrukcja[1]
                if isinstance(czytana, tuple):
                    if czytana[0] == "tablica":
                        if czytana[2] in self.propagacja and not self.zmienna_w_bloku[czytana[2]]:
                            czytana = (czytana[0], czytana[1], self.propagacja[czytana[2]], czytana[3]) 
                
                dodaj = ("read", czytana)
                nowe_istrukcje.append(dodaj)
            else:
                nowe_istrukcje.append(instrukcja)
            
        return nowe_istrukcje


    def te_same_instrukcje(self, instrukcja1, instrukcja2):
        """
            wersja alfa
        """
        if len(instrukcja1) != len(instrukcja2):
            return False
        for i in range(len(instrukcja1)):
            instr1 = instrukcja1[i]
            instr2 = instrukcja2[i]
            nazwa_instr1 = instr1[0]
            nazwa_instr2 = instr2[0]

            if nazwa_instr1 != nazwa_instr2:
                return False
            
            if nazwa_instr1 == "przypisz":
                zmienna1 = instr1[1]
                wyrazenie1 = instr1[2]
                nazwa_zmiennej1 = zmienna1[1]

                zmienna2 = instr2[1]
                wyrazenie2 = instr2[2]
                nazwa_zmiennej2 = zmienna2[1]
                if nazwa_zmiennej1 != nazwa_zmiennej2:
                    return False

                if len(wyrazenie1) == 2:
                    x1 = wyrazenie1[1]
                    x2 = wyrazenie2[1]

                    if type(x1) != type(x2):
                        return False
                    
                    if isinstance(x1, tuple):
                        if x1[0] != x2[0]:
                            return False
                        if x1[0] == "zmienna":
                            if x1[1] != x2[1]:
                                return False
                else:
                    x1 = wyrazenie1[2]
                    y1 = wyrazenie1[3]
                    x2 = wyrazenie2[2]
                    y2 = wyrazenie2[3]
                    
                    tx1 = type(x1)
                    tx2 = type(x2) 
                    ty1 = type(y1)  
                    ty2 = type(y2)  
                    
                    if wyrazenie1[1] != wyrazenie2[1]:
                        return False

                    if tx1 != tx2 and tx1 != ty2:
                        return False

                    if ty1 != ty2 and ty1 != tx2:
                        return False

                    if isinstance(x1, tuple):
                        if x1[0] != x2[0] and x1[0] != y2[0]:
                            return False
                        if y1[0] != y2[0] and y1[0] != x2[0]:
                            return False

                        if x1[0] == "zmienna" and x2[0] == "zmienna":
                            if x1[1] != x2[1] and x1[1] != y2[1]:
                                return False
                            if y1[1] != y2[1] and y1[1] != x2[1]:
                                return False
                        else:
                            return False  #TODO rozwinac
            else:
                return False #TODO rozwinac
        return True

 
    def usun_glupie(self, instrukcje):
        nowe_istrukcje = []
        for instrukcja in instrukcje:
            nazwa_instrukcji = instrukcja[0]
   
            if nazwa_instrukcji == "for_to" or nazwa_instrukcji == "for_downto":
                start = instrukcja[2]
                koniec = instrukcja[3]
                niwb = self.usun_glupie(instrukcja[4])
                if niwb:
                    if isinstance(start, int) and isinstance(koniec, int):
                        if nazwa_instrukcji == "for_to" and koniec - start < 10000:
                            dodaj = []
                            for x in range(start, koniec +1):
                                it = ("przypisz", ("zmienna", instrukcja[1], instrukcja[5]), ("wyrazenie", x))
                                self.deklaracje.append(("zmienna", instrukcja[1], instrukcja[5]))
                                dodaj.append(it)
                                for i in niwb:
                                    dodaj.append(i)
                            nowe_istrukcje.extend(dodaj)
                        elif nazwa_instrukcji == "for_downto" and start - koniec< 10000:
                            dodaj = []
                            for x in range(start, koniec-1 , -1):
                                it = ("przypisz", ("zmienna", instrukcja[1], instrukcja[5]), ("wyrazenie", x))
                                self.deklaracje.append(("zmienna", instrukcja[1], instrukcja[5]))
                                dodaj.append(it)
                                for i in niwb:
                                    dodaj.append(i)
                            nowe_istrukcje.extend(dodaj)
                        else:
                            dodaj = (nazwa_instrukcji, instrukcja[1], start, koniec, niwb, instrukcja[5])
                            nowe_istrukcje.append(dodaj)
                    else:
                        dodaj = (nazwa_instrukcji, instrukcja[1], start, koniec, niwb, instrukcja[5])
                        nowe_istrukcje.append(dodaj)

            elif nazwa_instrukcji == "while":
                niwb = self.usun_glupie(instrukcja[2])
                dodaj = (nazwa_instrukcji, instrukcja[1], niwb)
                nowe_istrukcje.append(dodaj)
            elif nazwa_instrukcji == "if_then":
                warunek = instrukcja[1]
                operator = warunek[1]
                x = warunek[2]
                y = warunek[3]
                if isinstance(x, int) and isinstance(y, int):
                    if operator == "=":
                        czy_prawda = (x == y)
                    elif operator == "!=":
                        czy_prawda = (x != y)
                    elif operator == "<":
                        czy_prawda = (x < y)
                    elif operator == "<=":
                        czy_prawda = (x <= y)
                    elif operator == ">":
                        czy_prawda = (x > y)
                    elif operator == ">=":
                        czy_prawda = (x >= y)
                    
                    if czy_prawda:
                        nowe_istrukcje.extend(instrukcja[2])
                else:
                    nowe_istrukcje.append(instrukcja)
            elif nazwa_instrukcji == "repeat_until":
                niwb = self.usun_glupie(instrukcja[1])
                dodaj = (nazwa_instrukcji, niwb, instrukcja[2])
                nowe_istrukcje.append(dodaj)
            elif nazwa_instrukcji == "if_then_else":
                warunek = instrukcja[1]
                operator = warunek[1]
                x = warunek[2]
                y = warunek[3]
                
                if self.te_same_instrukcje(instrukcja[2], instrukcja[3]):
                    nowe_istrukcje.extend(instrukcja[2])
                elif isinstance(x, int) and isinstance(y, int):
                    if operator == "=":
                        czy_prawda = (x == y)
                    elif operator == "!=":
                        czy_prawda = (x != y)
                    elif operator == "<":
                        czy_prawda = (x < y)
                    elif operator == "<=":
                        czy_prawda = (x <= y)
                    elif operator == ">":
                        czy_prawda = (x > y)
                    elif operator == ">=":
                        czy_prawda = (x >= y)
                    
                    if czy_prawda:
                        nowe_istrukcje.extend(instrukcja[2])
                    else:
                        nowe_istrukcje.extend(instrukcja[3])
                else:
                    nowe_istrukcje.append(instrukcja)

            elif nazwa_instrukcji == "przypisz":
                glupie = False
                zmienna = instrukcja[1]
                wyrazenie = instrukcja[2]
                nazwa_zmiennej = zmienna[1]

                if len(wyrazenie) == 2:
                    x = wyrazenie[1]
                    if isinstance(x, tuple):
                        if x[0] == "zmienna" and x[1] == nazwa_zmiennej:
                            glupie = True
                        if x[0] == "tablica" and x[1] == nazwa_zmiennej:
                            if x[2] == zmienna[2]:
                                glupie = True
                if not glupie:
                    nowe_istrukcje.append(instrukcja)
                
            else:
                nowe_istrukcje.append(instrukcja)
        return nowe_istrukcje

    def wyrzuc_blad(self, tresc):
        print(tresc)
        exit(-1)