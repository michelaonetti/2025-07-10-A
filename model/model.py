import copy

import networkx as nx

from database.DAO import DAO


class Model:
    def __init__(self):
        self._graph = nx.DiGraph()  # grafico diretto e pesato, per i pesi aggiungo weight=
        self._categories = DAO.getAllCategory()  # preno dao DAO con query tutti le category
        self._nodes = None
        self._AllProdotti = DAO.getAllProdotti()
        self._idMap = {}
        for n in self._AllProdotti:
            # inserico nella id map cosi poi ripesco da qua per ritornare ai valori dell'oggeto prodotto
            self._idMap[n.product_id] = n
        self._bestCammino = []
        self._bestScore = 0

    def buildGraph(self, category, start, end):
        self._graph.clear()
        list_nodi = DAO.getAllNodi(category)
        for oggetto in list_nodi:
            self._graph.add_node(oggetto)
        # aggiunge gli archi
        self.addEdges(category, start,end)  # carica in automatico gli archi

    def addEdges(self, category, start, end):
        self._graph.clear_edges()
        all_combinazioni = DAO.getAllProdottiVendutiTempo(
            category,start, end, self._idMap)  # tutte le combinaz di artisti di cui uno utente ne ha comprati
        """arco uscente dal nodo con numero di vendite maggiore
            arco entrante nel nodo con numero di vendite minore.
            parità di numero di vendite: si inseriscano entrambi gli archi.
            se un nodo NON sia stato venduto nel range selezionato, quel nodo deve rimanere isolato. 
            
            Il peso arco è pari alla somma delle vendite dei prodotti nel range considerato """
        for c in all_combinazioni:
            prodottoA = c[0].product_id
            venA = c[1]
            for c2 in all_combinazioni:
                prodottoB = c2[0].product_id
                venB = c2[1]
                if int(venA)!=0 and int(venB)!=0 and prodottoA != prodottoB:
                    if int(venA)>int(venB):
                        self._graph.add_edge(c[0], c2[0], weight=(int(venA)+int(venB)))
                    elif int(venA)<int(venB):
                        self._graph.add_edge(c2[0],c[0], weight=(int(venA)+int(venB)))
                    else:
                        self._graph.add_edge(c[0], c2[0], weight=(int(venA) + int(venB)))
                        self._graph.add_edge(c2[0],c[0], weight=(int(venA)+int(venB)))
                else:
                    continue #sono nel caso uno dei due è zero,ma quei nodi li ho già dentro al grafo

    def get_top_5_edges(self):
        """Ritorna i 5 archi con il peso maggiore"""
        # Ordina tutti gli archi in base all'attributo 'weight' decrescente
        prodotti_score = {}

        # Per ogni nodo nel grafo
        for nodo in self._graph.nodes():
            # Somma dei pesi degli archi USCENTI
            out_weight = 0
            for u, v, data in self._graph.out_edges(nodo, data=True):
                out_weight += data.get('weight', 0)

            # Somma dei pesi degli archi ENTRANTI
            in_weight = 0
            for u, v, data in self._graph.in_edges(nodo, data=True):
                in_weight += data.get('weight', 0)

            # Score = uscenti - entranti
            score = out_weight - in_weight
            prodotti_score[nodo] = {
                'score': score,
                'out_weight': out_weight,
                'in_weight': in_weight
            }

        # Ordina per score decrescente e prendi i top 5
        top_5 = sorted(prodotti_score.items(), key=lambda x: x[1]['score'], reverse=True)[:5]

        return top_5

    def getNumNodes(self):
        return len(self._graph.nodes)

    def getNumEdges(self):
        return len(self._graph.edges)

    def getDateRange(self):
        return DAO.getDateRange()


    def getCamminoOttimo(self, v0, v1, t):

        self._bestCammino = []
        self._bestScore = 0

        parziale = [v0]

        self._ricorsione(parziale, v1, t)
        print("sono uscita dalla ricorsione")
        return self._bestCammino, self._bestScore

    def _ricorsione(self, parziale, v1, t):
        print("entro nella ricorsione")
        if len(parziale) == t:
            # Controlla se siamo arrivati a destinazione
            if parziale[-1] == v1 and self._getScore(parziale) > self._bestScore:
                    self._bestCammino = copy.deepcopy(parziale)
                    self._bestScore = self._getScore(parziale)
                    return  # Non espandere oltre la lunghezza richiesta
        else:
            # espando parziale e faccio ricorsione con backtracking
            for n in self._graph.successors(parziale[-1]):
                if n not in parziale:
                    parziale.append(n)
                    self._ricorsione(parziale, v1, t)
                    parziale.pop()

    def _getScore(self, parziale):
        sumPesi = 0
        for i in range(0, len(parziale) - 1):
            sumPesi += self._graph[parziale[i]][parziale[i + 1]]["weight"]
        return sumPesi