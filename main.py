"""Atividade Pratica 01 - processamento sequencial e paralelo."""

from concurrent.futures import ProcessPoolExecutor
import argparse
import json
import os
import platform
import statistics
import time
from datetime import datetime


PROCESSOS = (2, 4, 8)
TAMANHOS_GRANULARIDADE = (20, 100, 500)


def tarefa(numero):
    """Tarefa de custo uniforme proposta nas etapas 1 e 2."""
    resultado = 0
    for i in range(1, 300_000):
        resultado += (numero * i) % 97
    return resultado


def tarefa_carga_desigual(numero):
    """Tarefa da etapa 6, com custo maior para multiplos de 10."""
    if numero % 10 == 0:
        limite = 1_500_000
    else:
        limite = 300_000

    resultado = 0
    for i in range(1, limite):
        resultado += (numero * i) % 97
    return resultado


def tarefa_carga_instrumentada(numero):
    """Executa a carga desigual e registra dados usados na analise."""
    inicio = time.perf_counter()
    resultado = tarefa_carga_desigual(numero)
    fim = time.perf_counter()
    return numero, resultado, os.getpid(), inicio, fim


def executar_sequencial(dados, funcao=tarefa):
    inicio = time.perf_counter()
    resultados = []
    for numero in dados:
        resultados.append(funcao(numero))
    fim = time.perf_counter()
    return resultados, fim - inicio


def executar_paralelo(dados, workers, funcao=tarefa):
    inicio = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as executor:
        resultados = list(executor.map(funcao, dados, chunksize=1))
    fim = time.perf_counter()
    return resultados, fim - inicio


def medir_repeticoes(executor, repeticoes):
    tempos = []
    ultimo_resultado = None

    for _ in range(repeticoes):
        ultimo_resultado, tempo_execucao = executor()
        tempos.append(tempo_execucao)

    return {
        "tempos": tempos,
        "media": statistics.mean(tempos),
        "desvio_padrao": statistics.stdev(tempos) if repeticoes > 1 else 0.0,
    }, ultimo_resultado


def experimentar_carga_uniforme(dados, repeticoes):
    sequencial, referencia = medir_repeticoes(
        lambda: executar_sequencial(dados), repeticoes
    )
    paralelos = {}

    for workers in PROCESSOS:
        medicao, resultados = medir_repeticoes(
            lambda workers=workers: executar_paralelo(dados, workers), repeticoes
        )
        if resultados != referencia:
            raise RuntimeError(f"Resultado incorreto na execucao com {workers} processos")

        speedup = sequencial["media"] / medicao["media"]
        medicao["speedup"] = speedup
        medicao["eficiencia"] = speedup / workers
        paralelos[str(workers)] = medicao

    return {
        "quantidade_tarefas": len(dados),
        "sequencial": sequencial,
        "paralelo": paralelos,
    }


def resumir_instrumentacao(registros, tempo_total):
    grupos = {}
    duracoes_leves = []
    duracoes_pesadas = []
    primeiro_inicio = min(registro[3] for registro in registros)

    for numero, _, pid, inicio, fim in registros:
        duracao = fim - inicio
        if numero % 10 == 0:
            duracoes_pesadas.append(duracao)
        else:
            duracoes_leves.append(duracao)

        grupo = grupos.setdefault(
            str(pid),
            {
                "tarefas": 0,
                "tarefas_pesadas": 0,
                "soma_duracoes": 0.0,
                "primeiro_inicio": inicio,
                "ultimo_fim": fim,
            },
        )
        grupo["tarefas"] += 1
        grupo["tarefas_pesadas"] += int(numero % 10 == 0)
        grupo["soma_duracoes"] += duracao
        grupo["primeiro_inicio"] = min(grupo["primeiro_inicio"], inicio)
        grupo["ultimo_fim"] = max(grupo["ultimo_fim"], fim)

    for grupo in grupos.values():
        grupo["inicio_relativo"] = grupo.pop("primeiro_inicio") - primeiro_inicio
        grupo["fim_relativo"] = grupo.pop("ultimo_fim") - primeiro_inicio

    return {
        "tempo_total": tempo_total,
        "media_tarefa_leve": statistics.mean(duracoes_leves),
        "media_tarefa_pesada": statistics.mean(duracoes_pesadas),
        "razao_pesada_leve": (
            statistics.mean(duracoes_pesadas) / statistics.mean(duracoes_leves)
        ),
        "por_processo": grupos,
    }


def experimentar_carga_desigual(dados, repeticoes):
    sequencial, referencia = medir_repeticoes(
        lambda: executar_sequencial(dados, tarefa_carga_desigual), repeticoes
    )
    paralelos = {}

    for workers in PROCESSOS:
        medicao, resultados = medir_repeticoes(
            lambda workers=workers: executar_paralelo(
                dados, workers, tarefa_carga_desigual
            ),
            repeticoes,
        )
        if resultados != referencia:
            raise RuntimeError(
                f"Resultado incorreto na carga desigual com {workers} processos"
            )

        speedup = sequencial["media"] / medicao["media"]
        medicao["speedup"] = speedup
        medicao["eficiencia"] = speedup / workers
        paralelos[str(workers)] = medicao

    inicio = time.perf_counter()
    with ProcessPoolExecutor(max_workers=4) as executor:
        registros = list(
            executor.map(tarefa_carga_instrumentada, dados, chunksize=1)
        )
    tempo_instrumentado = time.perf_counter() - inicio

    if [registro[1] for registro in registros] != referencia:
        raise RuntimeError("Resultado incorreto na execucao instrumentada")

    return {
        "quantidade_tarefas": len(dados),
        "sequencial": sequencial,
        "paralelo": paralelos,
        "instrumentacao_4_processos": resumir_instrumentacao(
            registros, tempo_instrumentado
        ),
    }


def mostrar_tabela(titulo, experimento):
    print(f"\n{titulo}")
    print("Processos | Tempo medio (s) | Speedup | Eficiencia")
    tempo_sequencial = experimento["sequencial"]["media"]
    print(f"        1 | {tempo_sequencial:15.6f} | {1.0:7.3f} | {1.0:10.3f}")

    for workers in PROCESSOS:
        medicao = experimento["paralelo"][str(workers)]
        print(
            f"{workers:9d} | {medicao['media']:15.6f} | "
            f"{medicao['speedup']:7.3f} | {medicao['eficiencia']:10.3f}"
        )


def executar_experimentos(repeticoes):
    dados_principais = list(range(1, 101))
    print(f"Executando testes principais ({repeticoes} repeticoes por configuracao)...")
    principal = experimentar_carga_uniforme(dados_principais, repeticoes)
    mostrar_tabela("Experimento principal - 100 tarefas", principal)

    granularidade = {}
    for tamanho in TAMANHOS_GRANULARIDADE:
        print(f"\nExecutando granularidade com {tamanho} tarefas...")
        experimento = experimentar_carga_uniforme(
            list(range(1, tamanho + 1)), repeticoes
        )
        granularidade[str(tamanho)] = experimento
        mostrar_tabela(f"Granularidade - {tamanho} tarefas", experimento)

    print("\nExecutando experimento de carga desigual...")
    carga_desigual = experimentar_carga_desigual(dados_principais, repeticoes)
    mostrar_tabela("Balanceamento - 100 tarefas", carga_desigual)

    return {
        "metodologia": {
            "data_hora": datetime.now().astimezone().isoformat(timespec="seconds"),
            "repeticoes": repeticoes,
            "estatistica": "media aritmetica",
            "python": platform.python_version(),
            "sistema": platform.platform(),
            "processadores_logicos": os.cpu_count(),
            "observacao": (
                "Os tempos paralelos incluem criacao do pool, distribuicao das "
                "tarefas e coleta dos resultados."
            ),
        },
        "experimento_principal": principal,
        "granularidade": granularidade,
        "carga_desigual": carga_desigual,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Executa todos os experimentos da Atividade Pratica 01."
    )
    parser.add_argument(
        "--repeticoes",
        type=int,
        default=3,
        help="numero de repeticoes por configuracao (padrao: 3)",
    )
    parser.add_argument(
        "--saida",
        default="resultados_brutos.json",
        help="arquivo JSON que recebera os resultados",
    )
    args = parser.parse_args()

    if args.repeticoes < 1:
        parser.error("--repeticoes deve ser maior ou igual a 1")

    resultados = executar_experimentos(args.repeticoes)
    with open(args.saida, "w", encoding="utf-8") as arquivo:
        json.dump(resultados, arquivo, ensure_ascii=False, indent=2)

    print(f"\nResultados brutos salvos em: {args.saida}")


if __name__ == "__main__":
    main()
