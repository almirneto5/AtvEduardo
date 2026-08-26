# Atividade Prática 01 – Processamento Sequencial e Paralelo

Este repositório contém o experimento da disciplina de Computação Paralela e
Distribuída. O objetivo é comparar a execução sequencial com a execução paralela
de uma tarefa computacional, observando tempo, speedup, eficiência, overhead,
granularidade e balanceamento de carga.

## Arquivos

- `main.py`: implementações sequencial e paralela e todos os experimentos.
- `resultados_brutos.json`: tempos individuais e dados usados nos cálculos.
- `resultados.md`: tabelas completas, respostas e análise dos resultados.

## Como executar

É necessário somente Python 3, sem bibliotecas externas.

```bash
python main.py
```

O programa faz três execuções por configuração e grava os dados em
`resultados_brutos.json`. Também é possível mudar esses parâmetros:

```bash
python main.py --repeticoes 3 --saida resultados_brutos.json
```

O bloco `if __name__ == "__main__":` foi utilizado para que o
`ProcessPoolExecutor` funcione corretamente também no Windows.

## Implementação e metodologia

A função `tarefa` realiza o laço de 1 até 299.999 definido no enunciado. A
versão sequencial percorre a lista normalmente, enquanto a versão paralela usa
`ProcessPoolExecutor.map` com 2, 4 e 8 processos. Os resultados das duas versões
são comparados automaticamente para garantir que o processamento paralelo não
alterou o cálculo.

Cada configuração foi executada três vezes e a tabela apresenta a média
aritmética. Os testes foram feitos em 26/08/2026, no Windows 11, com Python
3.13.8 e 8 processadores lógicos. O tempo paralelo inclui criação do pool,
distribuição das tarefas e coleta dos resultados.

## Resultados principais

| Processos | Tempo médio (s) | Speedup | Eficiência |
|---:|---:|---:|---:|
| 1 | 1,884752 | 1,000 | 100,0% |
| 2 | 1,313490 | 1,435 | 71,7% |
| 4 | 0,757043 | 2,490 | 62,2% |
| 8 | 0,834845 | 2,258 | 28,2% |

Foram usadas as fórmulas `Speedup = T1 / Tp` e
`Eficiência = Speedup / N`. O melhor tempo desse teste ocorreu com 4 processos.
Com 8 processos, o tempo aumentou 0,077802 s em relação a 4 processos, mostrando
que o custo adicional não foi compensado por mais paralelismo.

## Conclusão

Os resultados confirmam que aumentar o número de processos não garante ganho
proporcional. No teste principal, o speedup máximo foi 2,490 com 4 processos;
com 8, a eficiência caiu para 28,2%. Quando a carga cresceu para 500 tarefas, o
overhead foi mais bem amortizado e o speedup com 8 processos chegou a 2,979.
Mesmo assim, criação e comunicação dos processos, escalonamento, parte serial e
desbalanceamento limitaram o resultado, como previsto pela Lei de Amdahl.

As tabelas de todas as execuções e as respostas de cada etapa estão em
[resultados.md](resultados.md).
