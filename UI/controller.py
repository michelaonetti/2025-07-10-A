import datetime

import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model
        self._category = None
        self._prodStart = None
        self._prodEnd = None

    def loadCategory(self, dd: ft.Dropdown()):
        categories = sorted(list(self._model._categories))
        for f in categories:
            dd.options.append(ft.dropdown.Option(text=f,
                                                 data=f,
                                                 on_click=self.read_DD_Category))
    def read_DD_Category(self, e):
        print("read_DD_Category called ")
        if e.control.data is None:
            self._category = None
        else:
            self._category = e.control.data

    def handleCreaGrafo(self, e):
        #qui creo i nodi e gli archi del grafo
        self._view.txt_result.controls.clear()

        if self._category is None or self._category == "":
            self._view.create_alert("Scegliere una categoria")
            return
        self._view.txt_result.controls.append(ft.Text(f"Scelta la categoria: {self._category}!"))

        # devo creare il grafo
        start = self._view._dp1.value  # Ritorna una stringa tipo "2016-01-18"
        end = self._view._dp2.value
        self._model.buildGraph(self._category, start,end)
        self._view.txt_result.controls.append(ft.Text("Grafo correttamente creato."))
        self._view.txt_result.controls.append(
            ft.Text(f"Il grafo contiene {self._model.getNumNodes()} nodi e {self._model.getNumEdges()} archi."))
        self._view.txt_result.controls.append(ft.Text(f"Il grafo contiene {self._model.getNumNodes()} no "))

        self.loadDropDown(self._view._ddProdStart)
        self.loadDropDown(self._view._ddProdEnd)
        self._view.update_page()


    def handleBestProdotti(self, e):
        for prodotto, stats in self._model.get_top_5_edges():
            self._view.txt_result.controls.append(ft.Text(f"{prodotto.product_name} with score: {stats["score"]}"))
        self._view.update_page()

    def loadDropDown(self, dd: ft.Dropdown()):
        if dd.label == "Start product":  # se dobbiamo popolar eil menu di partenza
            for f in self._model._graph.nodes:
                dd.options.append(ft.dropdown.Option(text=f.product_name,
                                                     data=f,
                                                     on_click=self.read_DD_ProductStart))
        elif dd.label == "End product":
            for f in self._model._graph.nodes:
                dd.options.append(ft.dropdown.Option(text=f.product_name,
                                                     data=f,
                                                     on_click=self.read_DD_ProductEnd))


    def read_DD_ProductStart(self, e):
        print("read_DD_ProductStart called ")
        if e.control.data is None:
            self._prodStart = None
        else:
            self._prodStart = e.control.data

    def read_DD_ProductEnd(self, e):
        print("read_DD_ProductEnd called ")
        if e.control.data is None:
            self._prodEnd = None
        else:
            self._prodEnd = e.control.data

    """identifichi un cammino ottimo tale per cui:
    - Il cammino parti dal nodo identificato come Start Product e termini nel nodo identificato come End Product;
    - La lunghezza del cammino sia pari a Lun, valore numerico fornito dall’utente nel campo “Lunghezza
    cammino”;
    - Il cammino attraversi gli archi rispettando i versi;
    - Un nodo non può essere attraversato più volte;
    - La somma dei pesi degli archi deve essere massima."""
    def handleCercaCammino(self, e):
        t = self._view._txtInLun.value
        try:
            tInt = int(t)
        except ValueError:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text(f"Il valore di t deve essere un intero positivo.", color="red"))
            return

        print("vado a cercare il cammino")
        path, score = self._model.getCamminoOttimo(self._prodStart, self._prodEnd, tInt)
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(
            ft.Text(f"Cammino fra {self._prodStart} e {self._prodEnd} trovato.", color="green"))
        self._view.txt_result.controls.append(
            ft.Text(f"Il cammino ha uno score complessivo pari a {score} e contiene i seguenti nodi:", color="green"))

        for p in path:
            self._view.txt_result.controls.append(
                ft.Text(p.product_name, color="green"))

        self._view.update_page()





    def setDates(self):
        first, last = self._model.getDateRange()

        self._view._dp1.first_date = datetime.date(first.year, first.month, first.day)
        self._view._dp1.last_date = datetime.date(last.year, last.month, last.day)
        self._view._dp1.current_date = datetime.date(first.year, first.month, first.day)

        self._view._dp2.first_date = datetime.date(first.year, first.month, first.day)
        self._view._dp2.last_date = datetime.date(last.year, last.month, last.day)
        self._view._dp2.current_date = datetime.date(last.year, last.month, last.day)
