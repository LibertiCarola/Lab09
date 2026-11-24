from database.parco_DAO import ParcoDAO
from database.escursione_DAO import EscursioneDAO
from database.punto_interesse_DAO import PuntoInteresseDAO
from model.escursione import Escursione


class Model:
    def __init__(self):
        self.escursioni_map = {}                        # Mappa ID escursione -> oggetti Escursione                     qui ci sono tutte le info
        self.punti_interesse_map = {}                   # Mappa ID punto di interesse -> oggetti PuntoInteresse

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # Aggiungere eventuali altri attributi

        # qui ci sono Cod relazioni
        self.Cod_Escursioni = {}                            # self.Cod_Escursioni[id_esc] = [id_pt_int]
        self.Cod_punti_interesse = {}                       # self.Cod_punti_interesse[id_pt_int] = [id_esc]

        self.relazioni = EscursioneDAO.get_escursioni_punti_interesse()
        self.escursioni_utili = []

        self.max_giorni = 0
        self.max_budget = 0

        # Caricamento
        self.load_escursioni()
        self.load_punti_interesse()
        self.load_relazioni()

    @staticmethod
    def load_parchi():
        """ Restituisce tutti i parchi disponibili """
        return ParcoDAO.get_parchi()

    def load_escursioni(self):
        """ Carica tutte le escursioni in un dizionario [id.escursione] = OggettoClasseEsc"""
        self.escursioni_map = EscursioneDAO.get_escursioni()

    def load_punti_interesse(self):
        """ Carica tutti i punti di interesse in un dizionario[id.puntoInteresse] = OggettoClassePtInt"""
        self.punti_interesse_map = PuntoInteresseDAO.get_punti_interesse()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra escursioni e punti di interesse e salvarle nelle strutture dati
            Collega escursione <-> punti di interesse.
            --> Ogni Escursione ha un set di PuntoInteresse.
            --> Ogni PuntoInteresse ha un set di Escursioni.
        """
        lista_Escursioni_PuntInteresse = EscursioneDAO.get_escursioni_punti_interesse() #otteniamo una lista di oggetti contenenti id.escursione e id.pt_Int
        if lista_Escursioni_PuntInteresse:
            for elemento in lista_Escursioni_PuntInteresse:
                if elemento is None or elemento["id_escursione"] is None or elemento["id_punto_interesse"] is None:
                    continue
                id_esc = elemento["id_escursione"]
                id_pt_int = elemento["id_punto_interesse"]

                if id_esc not in self.Cod_Escursioni:                   # self.Cod_Escursioni[id_esc] = [id_pt_int]
                    self.Cod_Escursioni[id_esc] = [id_pt_int]
                else:
                    self.Cod_Escursioni[id_esc].append(id_pt_int)

                if id_pt_int not in self.Cod_punti_interesse:           # self.Cod_punti_interesse[id_pt_int] = [id_esc]
                    self.Cod_punti_interesse[id_pt_int] = [id_esc]
                else:
                    self.Cod_punti_interesse[id_pt_int].append(id_esc)


    def genera_pacchetto(self, id_parco: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto di escursioni ottimale per un parco rispettando i vincoli di durata, budget e punti di interesse unici.
        :param id_parco: id del parco
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Escursione)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il voto complessivo dei visitatori per il pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        self.max_giorni = max_giorni
        self.max_budget = max_budget


        self.escursioni_utili.clear()

        for esc in self.escursioni_map:
            esc_ogg = self.escursioni_map[esc]
            attrazioni = {}
            if esc_ogg.id_parco == id_parco:                                                     #lista pt_interesse
                self.escursioni_utili.append([esc_ogg.id, esc_ogg.nome, esc_ogg.durata_giorni, esc_ogg.costo, attrazioni])               # abbiamo una lista di liste con info escursioni

        if self.relazioni:
            for rel in self.relazioni:
                ID_esc = rel["id_escursione"]
                ID_pt_int = rel["id_punto_interesse"]
                NOME_pt_int = self.punti_interesse_map[ID_pt_int].nome
                voto_pt_int = self.punti_interesse_map[ID_pt_int].voto_visitatori

                for escursione in self.escursioni_utili:
                    if escursione[0] == ID_esc:
                        escursione[4][ID_pt_int] = [NOME_pt_int, voto_pt_int]         # escursioni_utili è ora una lista con stottoliste-escursione e sotto-dizionario punti-interesse
                                    # esc_0           # esc_1           ...
    # abbiamo escursioni_utili = [[info, dict[COD_pt_int] = [nome, voto], ...]   ->  entriamo nella ricorsione
        self._ricorsione(0, [], 0, 0, 0, set())
        self.completamento_pacchetto_ottimo()
        return self._pacchetto_ottimo, self._costo, self._valore_ottimo



    def _ricorsione(self, indice_escursione: int, pacchetto_parziale: list, durata_parziale: int, costo_parziale: float, punteggio_parziale: int, punti_interesse_inclusi: set):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il voto complessivo dei visitatori"""

        # è possibile cambiare i parametri formali della funzione se ritenuto opportuno

    #1. controlla che il pacchetto corrente sia il migliore altrimenti li aggiorna
        if punteggio_parziale > self._valore_ottimo:                            #possiamo fare questa operazione perché ala fine di ogni ciclo controlliamo che non superi prezzo e durata, quindi avremo in imput tutti dati accettabili
            self._valore_ottimo = punteggio_parziale
            self._pacchetto_ottimo = pacchetto_parziale.copy()
            self._costo = costo_parziale

    #2. ciclo for per controllare tutte le combinazioni a partire dall'indice corrente
        for i in range(indice_escursione, len(self.escursioni_utili)):
            esc = self.escursioni_utili[i]

            ID_esc_corrente = esc[0]
            durata_esc_corrente = esc[2]
            costo_esc_corrente = esc[3]

            somma_voti = 0
            id_attivita_incluse = set()

            for key_attivita in esc[4]:  # qui lavoriamo con i punti d'interesse nel diz
                ID_attivita = key_attivita
                id_attivita_incluse.add(ID_attivita)
                voto = esc[4][key_attivita][1]
                somma_voti += voto

    #3. verifica vincoli per ogni combinazione
            nuovo_costo = costo_parziale + costo_esc_corrente
            nuova_durata = durata_parziale + durata_esc_corrente

            budget_ok = (self.max_budget is None) or (nuovo_costo <= self.max_budget)
            giorni_ok = (self.max_giorni is None) or (nuova_durata <= self.max_giorni)

            if budget_ok and giorni_ok:
                if id_attivita_incluse.isdisjoint(punti_interesse_inclusi):  # se non ci sono punti d'interesse inclusi
    #4. aggiorna
                    pacchetto_parziale.append(ID_esc_corrente)
                    attivita_esc_correnti = punti_interesse_inclusi.copy().union(id_attivita_incluse)
                    self._ricorsione(i+1, pacchetto_parziale, nuova_durata, nuovo_costo, punteggio_parziale+somma_voti, attivita_esc_correnti)

    #5. BACKTRACKING: rimuovi l'ultima escursione e testa quella dopo
                    pacchetto_parziale.pop()

    def completamento_pacchetto_ottimo(self):
        lista = []
        for codice in self._pacchetto_ottimo:
            oggetto = self.escursioni_map[codice]

            for escursione in self.escursioni_utili:
                if escursione[0] == codice:
                    lista_finale = []

                    for attrazione in escursione[4].values():
                        stringa = f'{attrazione[0]} ({attrazione[1]})'
                        lista_finale.append(stringa)
                    oggetto.punti_interesse = lista_finale
            lista.append(oggetto)

        self._pacchetto_ottimo = lista
