"""main.py - Interface de terminal do sistema especialista CellCare."""
from motor import Motor, carregar_base, LIMIAR_DIAG

LARGURA = 66

BANNER = f"""
╔{"═" * LARGURA}╗
║  📱 CELLCARE ASSISTÊNCIA TÉCNICA — TRIAGEM INTELIGENTE           ║
║  Sistema especialista para diagnóstico de defeitos em celulares  ║
║  com recomendação de reparo e explicação do raciocínio.          ║
╠{"═" * LARGURA}╣
║  Opções de resposta durante o questionário:                      ║
║    s (sim) | n (não) | t (talvez) | ? (não sei)                  ║
║    p (por que esta pergunta?)     | sair (encerrar programa)     ║
╚{"═" * LARGURA}╝"""

ROTULOS_NEGADOS = {
    "liga": "aparelho não liga",
    "molhou": "sem contato com líquido",
    "caiu": "sem queda recente",
    "carrega": "não carrega quando conectado",
    "conector_folgado": "conector firme (sem folga)",
    "armazenamento_cheio": "armazenamento com espaço livre",
    "wifi_falha": "Wi-Fi funciona normalmente",
    "idade_alta": "aparelho com menos de 2 anos de uso",
}


def barra_certeza(cf, tamanho=28):
    """Gera uma barra visual de progresso para o fator de certeza."""
    preenchidos = round(cf * tamanho)
    vazio = tamanho - preenchidos
    return f"[{'█' * preenchidos}{'░' * vazio}] {cf:.0%}"


def formatar_sinal(premissa, motor):
    """Formata uma premissa (positiva ou negada) de forma legível."""
    negada = premissa.startswith("!")
    nome = premissa.lstrip("!")
    if negada:
        return ROTULOS_NEGADOS.get(nome, f"não ({motor._rotulo(nome)})")
    return motor._rotulo(nome)


def coletar_sinais(motor, fato):
    """Coleta os fatos informados pelo cliente que embasaram um diagnóstico."""
    sinais = []
    derivado = motor.derivados.get(fato)
    if not derivado:
        return sinais
    for uso in derivado["usos"]:
        for premissa in uso["premissas"]:
            nome = premissa.lstrip("!")
            if nome in motor.derivados:
                for s in coletar_sinais(motor, nome):
                    if s not in sinais:
                        sinais.append(s)
            else:
                texto = formatar_sinal(premissa, motor)
                if texto not in sinais:
                    sinais.append(texto)
    return sinais


def exibir_por_que(motor, pergunta):
    """Exibe uma explicação detalhada e formatada do motivo da pergunta."""
    fato = pergunta["fato"]
    print(f"\n  ┌─ POR QUE PERGUNTO ISSO? {'─' * 39}")
    if pergunta.get("tipo") == "numero":
        fatos_gerados = list(pergunta.get("gera", {}).keys())
        regras_rel = [
            r for r in motor.regras
            if any(fg in [p.lstrip("!") for p in r["se"]] for fg in fatos_gerados)
        ]
        print("  │ O tempo de uso ajuda a avaliar o desgaste natural de componentes.")
        if regras_rel:
            print(f"  │ Essa informação é utilizada em {len(regras_rel)} regra(s) de inferência:")
            for r in regras_rel[:4]:
                alvo = motor._rotulo(r["entao"])
                print(f"  │   • [{r['id']}] {r['descricao']} -> investiga: {alvo}")
    else:
        usam = [r for r in motor.regras if fato in [p.lstrip("!") for p in r["se"]]]
        if not usam:
            print("  │ Esta informação ajuda a contextualizar o atendimento e filtrar")
            print("  │ as próximas perguntas da triagem.")
        else:
            print(f"  │ A informação sobre '{motor._rotulo(fato)}' é avaliada em {len(usam)} regra(s):")
            for r in usam[:4]:
                alvo = motor._rotulo(r["entao"])
                print(f"  │   • [{r['id']}] {r['descricao']}")
                print(f"  │          └─ Ajuda a verificar: {alvo} (peso {r['cf']:.0%})")
            if len(usam) > 4:
                print(f"  │   ... e mais {len(usam) - 4} regra(s).")
    print(f"  └{'─' * 64}")


def exibir_como(motor, fato):
    """Exibe passo a passo como o motor de inferência chegou ao diagnóstico."""
    d_info = motor.diagnosticos.get(fato, {})
    titulo = d_info.get("titulo", motor._rotulo(fato))
    certeza_final = motor.derivados.get(fato, {}).get("cf", 0.0)

    print(f"\n  ╔═ COMO CHEGAMOS À CONCLUSÃO: {titulo.upper()} ")
    print(f"  ║ Certeza combinada final: {certeza_final:.0%}")
    print(f"  ╠{'═' * 64}")

    def _detalhar(f_atual, nivel=0):
        deriv = motor.derivados.get(f_atual)
        recuo = "  ║ " + ("    " * nivel)
        if not deriv:
            return
        for idx, uso in enumerate(deriv["usos"], 1):
            regra = motor._regra(uso["regra"])
            print(f"{recuo}▸ Passo {idx} — Regra [{regra['id']}]: {regra['descricao']}")
            print(f"{recuo}  Confiança da regra: {regra['cf']:.0%} | Certeza obtida neste passo: {uso['cf']:.0%}")
            print(f"{recuo}  Condições avaliadas:")
            for prem, val in uso["premissas"].items():
                nome = prem.lstrip("!")
                if nome in motor.derivados:
                    print(f"{recuo}    • Hipótese intermediária: {motor._rotulo(nome)} (certeza {val:.0%})")
                    _detalhar(nome, nivel + 2)
                else:
                    sinal = formatar_sinal(prem, motor)
                    print(f"{recuo}    • Fato informado: {sinal} (confiança {val:.0%})")

    _detalhar(fato)
    print(f"  ╚{'═' * 64}")


def exibir_resumo_respostas(motor, historico_respostas):
    """Apresenta um resumo organizado das respostas fornecidas pelo cliente."""
    print("\n" + "─" * (LARGURA + 2))
    print("  📋 RESUMO DAS RESPOSTAS DO CLIENTE")
    print("─" * (LARGURA + 2))

    if not historico_respostas:
        print("  Nenhuma informação específica foi confirmada durante a triagem.")
        return

    confirmados = [item for item in historico_respostas if item["tipo"] == "sim"]
    incertos = [item for item in historico_respostas if item["tipo"] == "talvez"]
    negados = [item for item in historico_respostas if item["tipo"] == "nao"]
    pulados = [item for item in historico_respostas if item["tipo"] == "pulou"]

    if confirmados:
        print("  ✔ Sinais confirmados (Sim):")
        for item in confirmados:
            print(f"    • {item['descricao']}")
    if incertos:
        print("  ? Sinais com dúvida (Talvez):")
        for item in incertos:
            print(f"    • {item['descricao']}")
    if negados:
        print("  ✖ Sinais descartados (Não):")
        for item in negados:
            print(f"    • {item['descricao']}")
    if pulados:
        print(f"  ⏭ Perguntas puladas (Não sei): {len(pulados)}")


def exibir_diagnosticos(motor, resultado):
    """Exibe os diagnósticos em blocos visuais organizados."""
    print(f"\n╔{'═' * LARGURA}╗")
    print(f"║  📱 CELLCARE{' ' * 37}RESULTADO FINAL ║")
    print(f"╚{'═' * LARGURA}╝")

    for idx, (fato, cf) in enumerate(resultado, 1):
        d = motor.diagnosticos[fato]
        sinais = coletar_sinais(motor, fato)
        sinais_texto = ", ".join(sinais) if sinais else "análise combinada dos sintomas"

        urgencia = d["urgencia"].upper()
        destaque_urgencia = f"⚠ URGÊNCIA {urgencia}" if urgencia == "ALTA" else f"Urgência: {d['urgencia']}"

        print(f"\n┌─ DIAGNÓSTICO #{idx} {'─' * (LARGURA - 18)}┐")
        print(f"│  {d['titulo'].upper()}")
        print(f"│  {destaque_urgencia}")
        print(f"│")
        print(f"│  Sinais identificados: {sinais_texto}.")
        print(f"│")
        print(f"│  Custo estimado: {d['custo']:<22} Prazo estimado: {d['prazo']}")
        print(f"│")
        print(f"│  Fator de certeza:")
        print(f"│  {barra_certeza(cf)}")
        print(f"│")
        print(f"│  Reparo sugerido: {d['acao']}")
        print(f"└{'─' * LARGURA}┘")


def perguntar(motor, pergunta, indice, total_estimado, historico_respostas):
    """Pergunta ao usuário até receber uma resposta válida, com mensagens de erro claras."""
    eh_numero = pergunta.get("tipo") == "numero"
    dica = "[número em anos | ? (não sei) | p (por que?) | sair]" if eh_numero else "[s/n/t/? | p (por que?) | sair]"

    while True:
        try:
            texto = input(f"\n[{indice}] {pergunta['texto']} {dica}\n> ").strip()
        except EOFError:
            raise SystemExit(0)

        t = texto.lower()
        if t == "sair":
            print("\nEncerrando o atendimento. Até logo!")
            raise SystemExit(0)

        if t in ("p", "porque", "por que", "por quê"):
            exibir_por_que(motor, pergunta)
            continue

        if not t:
            print("  ⚠ Entrada vazia! Por favor, digite uma resposta antes de pressionar Enter.")
            if eh_numero:
                print("    Dica: informe os anos de uso (ex.: 1, 2.5) ou '?' se não souber.")
            else:
                print("    Dica: digite 's' para sim, 'n' para não, 't' para talvez ou '?' se não souber.")
            continue

        try:
            respondeu = motor.aplicar(pergunta, texto)
            # Registra no histórico para o resumo do cliente
            if not respondeu:
                historico_respostas.append({
                    "tipo": "pulou",
                    "descricao": pergunta["texto"]
                })
            elif eh_numero:
                valor = float(t.replace(",", "."))
                anos_str = f"{valor:g} ano(s)"
                historico_respostas.append({
                    "tipo": "sim",
                    "descricao": f"Tempo de uso informado: {anos_str}"
                })
            else:
                rotulo = motor._rotulo(pergunta["fato"])
                cf_informado = motor.fatos.get(pergunta["fato"], 0.0)
                if cf_informado == 1.0:
                    historico_respostas.append({"tipo": "sim", "descricao": rotulo.capitalize()})
                elif cf_informado == 0.5:
                    historico_respostas.append({"tipo": "talvez", "descricao": rotulo.capitalize()})
                else:
                    historico_respostas.append({"tipo": "nao", "descricao": rotulo.capitalize()})
            return
        except ValueError as erro:
            print(f"  ✖ Entrada inválida ({texto!r}): {erro}")
            if eh_numero:
                print("    💡 Exemplo válido: digite '2' para dois anos, '1.5' para um ano e meio, ou '?' para pular.")
            else:
                print("    💡 Opções aceitas: 's' (sim), 'n' (não), 't' (talvez), '?' (não sei) ou 'p' (explicação).")


def menu_pos_triagem(motor, resultado):
    """Exibe o menu após a triagem, permitindo reiniciar mesmo sem diagnóstico."""
    while True:
        if resultado:
            opcoes_texto = "\n[1] Como chegamos a essa conclusão?  [2] Nova triagem  [0] Sair\n> "
            opcoes_validas = ("1", "2", "0")
        else:
            opcoes_texto = "\n[1] Realizar nova triagem  [0] Sair\n> "
            opcoes_validas = ("1", "0")

        try:
            op = input(opcoes_texto).strip()
        except EOFError:
            return False

        if resultado:
            if op == "1":
                for fato, _ in resultado:
                    exibir_como(motor, fato)
            elif op == "2":
                return True
            elif op == "0" or op.lower() == "sair":
                return False
            else:
                print(f"  ✖ Opção '{op}' inválida! Escolha uma das opções disponíveis: {', '.join(opcoes_validas)}.")
        else:
            if op == "1":
                return True
            elif op == "0" or op.lower() == "sair":
                return False
            else:
                print(f"  ✖ Opção '{op}' inválida! Digite 1 para iniciar uma nova triagem ou 0 para sair.")


def triagem(motor):
    """Executa um ciclo completo de perguntas, resumo e apresentação de diagnóstico."""
    motor.reiniciar()
    historico_respostas = []
    indice = 1

    for pergunta in motor.base["perguntas"]:
        if motor.aplicavel(pergunta):
            perguntar(motor, pergunta, indice, len(motor.base["perguntas"]), historico_respostas)
            indice += 1

    exibir_resumo_respostas(motor, historico_respostas)
    resultado = motor.inferir()

    if not resultado:
        print(f"\n┌{'─' * LARGURA}┐")
        print("│  🔍 RESULTADO DA TRIAGEM: DIAGNÓSTICO INCONCLUSIVO               │")
        print(f"├{'─' * LARGURA}┤")
        print("│  Não foi possível concluir um diagnóstico com certeza suficiente │")
        print("│  a partir das informações fornecidas.                            │")
        print("│                                                                  │")
        print("│  Recomendação: encaminhar o aparelho para análise técnica        │")
        print("│  presencial na bancada da CellCare.                              │")
        print(f"└{'─' * LARGURA}┘")
        return menu_pos_triagem(motor, resultado)

    exibir_diagnosticos(motor, resultado)
    return menu_pos_triagem(motor, resultado)


def main():
    motor = Motor(carregar_base())
    print(BANNER)
    while triagem(motor):
        print("\n" + "═" * (LARGURA + 2))
        print("  🔄 INICIANDO NOVA TRIAGEM...")
        print("═" * (LARGURA + 2))
    print("\nObrigado por usar o CellCare!")


if __name__ == "__main__":
    main()
