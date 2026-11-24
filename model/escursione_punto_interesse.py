from dataclasses import dataclass, field

@dataclass()
class EscursionePuntoInteresse:
    id_escursione : str
    id_punto_interesse : str

    def __eq__(self, other):
        return isinstance(other, Escursione) and self.id == other.id

    def __str__(self):
        return f"{self.nome} | Durata: {self.durata_giorni} giorni | Costo: €{round(self.costo, 2)}"

    def __repr__(self):
        return f"{self.nome} | Durata: {self.durata_giorni} giorni | Costo: €{round(self.costo, 2)}"

    def __hash__(self):
        return hash(self.id)
