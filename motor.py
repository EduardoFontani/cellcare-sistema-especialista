"""
motor.py - Motor de inferência do sistema especialista CellCare.

Técnica: ENCADEAMENTO PARA FRENTE (forward chaining) com FATORES DE CERTEZA.
  1. Partimos dos fatos informados pelo usuário (memória de trabalho).
  2. Disparamos toda regra cujas premissas estão satisfeitas.
  3. As conclusões viram novos fatos e podem disparar outras regras.
  4. Repetimos até nada mais mudar (ponto fixo).
"""
import json
from pathlib import Path

LIMIAR = 0.2        # certeza mínima para uma premissa valer como verdadeira
LIMIAR_DIAG = 0.4   # certeza mínima para recomendar um diagnóstico

RESPOSTAS = {"s": 1.0, "sim": 1.0, "n": 0.0, "nao": 0.0, "não": 0.0, "t": 0.5, "talvez": 0.5}
PULAR = {"?", "ns", "nao sei", "não sei"}



def carregar_base(caminho="base_conhecimento.json"):
    """Lê a base de conhecimento de um arquivo JSON."""
    caminho_arquivo = Path(caminho)

    if not caminho_arquivo.is_absolute():
        caminho_arquivo = Path(__file__).resolve().parent / caminho_arquivo

    with open(caminho_arquivo, encoding="utf-8") as arq:
        base = json.load(arq)

    ids = [r["id"] for r in base["regras"]]

    if len(ids) != len(set(ids)):
        raise ValueError("Base inválida: existem regras com id repetido.")

    return base



def combinar(cf1, cf2):
    """Combina duas evidências a favor da mesma conclusão (fórmula do MYCIN)."""
    return cf1 + cf2 * (1 - cf1)


class Motor:
    def __init__(self, base):
        self.base = base
        self.regras = base["regras"]
        self.diagnosticos = base["diagnosticos"]
        self.rotulos = base["rotulos"]
        self.fatos = {}      # fatos do usuário: nome -> certeza (0 a 1)
        self.derivados = {}  # fatos deduzidos: nome -> {"cf": x, "usos": [...]}

    # ---------- memória de trabalho ----------
    def reiniciar(self):
        self.fatos, self.derivados = {}, {}

    def informar(self, fato, cf):
        self.fatos[fato] = max(0.0, min(1.0, float(cf)))

    def _valor(self, premissa):
        """Certeza da premissa. '!x' significa 'x é falso'. None = desconhecido."""
        negada = premissa.startswith("!")
        nome = premissa.lstrip("!")
        if nome in self.fatos:
            cf = self.fatos[nome]
        elif nome in self.derivados:
            cf = self.derivados[nome]["cf"]
        else:
            return None
        return 1 - cf if negada else cf

    # ---------- entrada do usuário ----------
    def aplicavel(self, pergunta):
        """A pergunta só é feita se as condições 'so_se' forem verdadeiras."""
        for cond in pergunta.get("so_se", []):
            v = self._valor(cond)
            if v is None or v < LIMIAR:
                return False
        return True

    def aplicar(self, pergunta, texto):
        """Interpreta a resposta. Levanta ValueError se for inválida.
        Retorna False se o usuário preferiu pular (não sei)."""
        t = texto.strip().lower()
        if pergunta.get("tipo") == "numero":
            if t in PULAR:
                return False
            try:
                valor = float(t.replace(",", "."))
            except ValueError:
                raise ValueError("Digite um número, por exemplo 2 ou 1.5.")
            if valor < 0 or valor > 30:
                raise ValueError("Digite um valor entre 0 e 30 anos.")
            for fato, lim in pergunta.get("gera", {}).items():
                ok = valor >= lim["min"] if "min" in lim else valor < lim["max"]
                self.informar(fato, 1.0 if ok else 0.0)
            return True
        if t in PULAR:
            return False
        if t not in RESPOSTAS:
            raise ValueError("Resposta inválida. Use s (sim), n (não), t (talvez) ou ? (não sei).")
        self.informar(pergunta["fato"], RESPOSTAS[t])
        return True

    # ---------- inferência ----------
    def inferir(self):
        """Encadeamento para frente até o ponto fixo. Retorna os diagnósticos."""
        self.derivados = {}
        for _ in range(len(self.regras) + 1):
            propostas = {}
            for r in self.regras:
                valores = [self._valor(p) for p in r["se"]]
                if any(v is None or v < LIMIAR for v in valores):
                    continue
                cf = min(valores) * r["cf"]
                propostas.setdefault(r["entao"], []).append(
                    {"regra": r["id"], "cf": cf, "premissas": dict(zip(r["se"], valores))})
            novos = {}
            for fato, usos in propostas.items():
                cf = 0.0
                for u in usos:
                    cf = combinar(cf, u["cf"])
                novos[fato] = {"cf": cf, "usos": usos}
            estavel = ({k: round(v["cf"], 6) for k, v in novos.items()} ==
                       {k: round(v["cf"], 6) for k, v in self.derivados.items()})
            self.derivados = novos
            if estavel:
                break
        return self.conclusoes()

    def conclusoes(self):
        """Lista (diagnóstico, certeza) acima do limiar, da maior para a menor."""
        lista = [(d, self.derivados[d]["cf"]) for d in self.diagnosticos
                 if d in self.derivados and self.derivados[d]["cf"] >= LIMIAR_DIAG]
        return sorted(lista, key=lambda x: -x[1])

    # ---------- explicação ----------
    def _regra(self, rid):
        return next(r for r in self.regras if r["id"] == rid)

    def _rotulo(self, fato):
        if fato in self.diagnosticos:
            return self.diagnosticos[fato]["titulo"]
        return self.rotulos.get(fato, fato)

    def como(self, fato, nivel=0):
        """Módulo 'COMO': mostra as regras e fatos usados para chegar à conclusão."""
        d = self.derivados.get(fato)
        pad = "    " * nivel
        if d is None:
            return [f"{pad}Nada foi concluído sobre '{fato}'."]
        linhas = [f"{pad}Conclusão: {self._rotulo(fato)} (certeza {d['cf']:.0%})"]
        for u in d["usos"]:
            r = self._regra(u["regra"])
            linhas.append(f"{pad}  Regra {r['id']}: {r['descricao']} (certeza da regra {r['cf']:.0%})")
            for prem, valor in u["premissas"].items():
                neg = prem.startswith("!")
                nome = prem.lstrip("!")
                if nome in self.derivados:
                    linhas.extend(self.como(nome, nivel + 2))
                else:
                    resp = "NÃO" if neg else "SIM"
                    linhas.append(f"{pad}      - {self._rotulo(nome)}: {resp} (certeza {valor:.0%})")
        return linhas

    def por_que(self, fato):
        """Módulo 'POR QUE': explica por que o sistema pergunta sobre este fato."""
        usam = [r for r in self.regras if fato in [p.lstrip("!") for p in r["se"]]]
        if not usam:
            return ["Esta informação ajuda a contextualizar o atendimento."]
        linhas = [f"Pergunto sobre '{self._rotulo(fato)}' porque ela é usada em {len(usam)} regra(s):"]
        for r in usam[:4]:
            linhas.append(f"  - {r['id']}: {r['descricao']}")
        return linhas
