"""main.py - Interface de terminal do sistema especialista CellCare."""
from motor import Motor, carregar_base, LIMIAR_DIAG

BANNER = """
==============================================================
  CellCare Assistência Técnica - Triagem Inteligente
  Sistema especialista que diagnostica defeitos de celulares
  e recomenda o reparo, com explicação do raciocínio.
==============================================================
Responda: s (sim) | n (não) | t (talvez) | ? (não sei) | p (por que pergunta?) | sair
"""


def perguntar(motor, pergunta):
    """Pergunta até receber uma resposta válida (tratamento de entradas inválidas)."""
    while True:
        try:
            texto = input(f"\n{pergunta['texto']}\n> ").strip()
        except EOFError:
            raise SystemExit(0)
        if texto.lower() == "sair":
            raise SystemExit(0)
        if texto.lower() in ("p", "porque", "por que"):
            print("\n".join(motor.por_que(pergunta["fato"])))
            continue
        try:
            motor.aplicar(pergunta, texto)
            return
        except ValueError as erro:
            print(f"  ! {erro}")


def triagem(motor):
    motor.reiniciar()
    for pergunta in motor.base["perguntas"]:
        if motor.aplicavel(pergunta):
            perguntar(motor, pergunta)
    resultado = motor.inferir()
    print("\n" + "=" * 62)
    if not resultado:
        print("Não foi possível concluir com as informações fornecidas.")
        print("Recomendação: encaminhar o aparelho para análise na bancada.")
        return
    print("DIAGNÓSTICOS SUGERIDOS")
    for fato, cf in resultado:
        d = motor.diagnosticos[fato]
        print(f"\n* {d['titulo']}  [certeza {cf:.0%} | urgência {d['urgencia']}]")
        print(f"  O que fazer: {d['acao']}")
        print(f"  Custo estimado: {d['custo']} | Prazo: {d['prazo']}")
    while True:
        op = input("\n[1] Como chegamos a essa conclusão?  [2] Nova triagem  [0] Sair\n> ").strip()
        if op == "1":
            for fato, _ in resultado:
                print("\n" + "\n".join(motor.como(fato)))
        elif op == "2":
            return True
        elif op == "0":
            return False
        else:
            print("  ! Opção inválida. Digite 1, 2 ou 0.")


def main():
    motor = Motor(carregar_base())
    print(BANNER)
    while triagem(motor):
        pass
    print("\nObrigado por usar o CellCare!")


if __name__ == "__main__":
    main()
