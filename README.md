# AUTOR: Artur Sikorski, 250086
Zadanie zaliczeniowe laboratorium kursu Języki Formalne i Techniki Translacji
prowadzonego w semestrze zimowym 2020/2021 przez dr. Maćka Gębalę.

# INSTALACJA:
Przykładowa instalacja

Update apt-get:

	sudo apt-get update

Instalacja Python3:
	
	sudo apt-get install python3

Instalacja PIP (menadżera plików):

	sudo apt-get install python3-pip

Instalacja Ply:

	python3 -m pip install ply


## URUCHOMIENIE:
	python3 kompilator.py [plik.imp] [plik.mr] [opcjonalna flaga -OOFF wylaczajaca optymalizacje]


# KROTKI OPIS DZIALANIA KOMPILATORA:

## LEXER (analiza_leksykalna.py):
Tworzy tokeny typu LexToken(LICZBA,'30',<nr_lini>, <nr_znaku>) potrzebne do
analizy skladniowej (parsowania)



## PARSER (analiza_skladniowa.py):
Tworzy drzewo parsowania zawierajace nastepujace wezly:
*       ("wyrazenie", liczba)
*	("wyrazenie", operator, x, y), gdzie x,y to liczba zmienna lub tablica
*	("zmienna", nazwa_zmiennej, nr_linii)
*	("tablica", nazwa_tablicy, indeks, nr_linii), gdzie indeks to liczba lub zmienna
*	("warunek", operator, x, y), gdie x,y to liczba, zmienna lub tablica
*	("przypisz", x, wyrazenie), gdzie x to zmienna lub tablica
*	("for_to", iterator, start, koniec, instrukcje_w_bloku, linia), gdzie start, koniec to liczba zmienna lub tablica
*	("for_downto", iterator, start, koniec, instrukcje_w_bloku, linia), a iterator to nazwa iteratora np. i
*	("while", warunek, instrukcje_w_bloku)
*	("repeat_until", instrukcje_w_bloku, warunek)
*	("if_then", warunek, instrukcje_w_bloku)
*	("if_then_else", warunek, instrukcje_w_bloku_prawdy, instrukcje_w_bloku_falszu)
*	("write", x), gdzie x to liczba, zmienna lub tablica
*	("read", x), gdzie x to zmienna lub tablica



## ANALIZATOR SEMANTYCZNY (analiza_semantyczna.py): 
Jego zadaniem jest zgłaszanie błędów w drzewie parsowanie, np. użycie niezainicjowanej nazwa_zmiennej,
albo użycie niewłaściwego zakresu pętli FOR czy modyfikowania iteratora w trakcie jej działania.



## OPTYMALIZATOR (optymalizator.py):
1. Wyliczanie wartosci stalych - zamiana wyrazeni typu a:= 32 + 4; na a:=36, lub x:= y * 1 na x:=y;
2. Propagacja stalych - zamienia wyrazenie typu a:= 3;, b:= 2 + a; na b:=5;
3. Eliminacja niepotrzebnych wyrazen - usuwanie przypisan nieuzywanych zmiennych a nawet calych blokow
4. itp...
Przyklady:

		DECLARE                                 DECLARE
			a, b, c                                 a
		BEGIN                                   BEGIN
			READ a;                                 READ a;
			FOR i FROM a TO 30 DO     	->          WRITE a;
				b := 43;                        END
				c := b + 34;
			ENDFOR
			WRITE a;
		END
		Koszt: 4535								Koszt: 202

		----------------------------------------------------

		DECLARE									DECLARE
			a,b,c,d									e
		BEGIN									BEGIN
			READ e;						->			READ e;
			c:= 0;									WRITE 7700;
			d := 0;									WRITE e;								
			a:= 3;								END
			b:=4;
			FOR i FROM 1 TO 20 DO			
				c := c + 1;
				FOR j FROM 42 DOWNTO 11 DO
					d := a * b;
					c := c + d;
				ENDFOR
			ENDFOR
			WRITE c;
			WRITE e;
		END
		Koszt: 252327 							Koszt: 353   (dla e = 10)

Optymalizator musi nieraz przejsc wielokrotnie po drzewie parsowania, jednak programy
nie powinny optymalizowac sie dluzej niz 5s, optymalizator nie powinien rowniez sie zapetlac :)
__Gdyby jednak kompilacja trwala zbyt dlugo zawsze mozna uzyc flagi -OOFF !!!__



## GRAF PRZEPLYWU STEROWANIA (graf_przeplywu_sterowania.py):
Jego zadaniem jest zamiana zlozonych instrukcji na latwiejsze do zamienienia na kod wynikowy.
Do tego celu uzywane sa m.in. znaczniki (ang. label). 
Np. instrukje ("if_then", warunek, instrukcje_w_bloku) mozna zamienic na:
1. dodaj do grafu: idz_do_jesli(warunek_przeciwny, znacznik_konca_ifa)
2. dodaj do grafu: instrukcje_w_bloku
3. dodaj do grafu: znacznik_konca_ifa
Znacznik w programie ma postac instukcji: ("znacznik", @licnzik_znacznikow)




## GENERATOR KODU MASZYNY WIRTUALNEJ (gnerator_kodu.py):
  Służy do zamiany instrukcji z grafu przeplywu na kod wynikowy. 



