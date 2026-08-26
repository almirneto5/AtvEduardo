# Resultados e análise

## Metodologia

Cada configuração foi executada três vezes. Usei a média aritmética porque os
tempos variaram um pouco entre as rodadas. Os testes foram realizados em
26/08/2026, no Windows 11, com Python 3.13.8 e 8 processadores lógicos. O tempo
medido na versão paralela inclui a criação do pool, a distribuição das tarefas e
a coleta dos resultados. Os valores individuais também estão preservados em
`resultados_brutos.json`.

## Etapa 1 – Processamento sequencial

Com `dados = list(range(1, 101))`, os tempos sequenciais foram:

| Execução 1 (s) | Execução 2 (s) | Execução 3 (s) | Média T1 (s) |
|---:|---:|---:|---:|
| 1,905334 | 1,886864 | 1,862059 | 1,884752 |

Esse tempo médio foi adotado como `T1` no experimento principal.

## Etapa 2 – Processamento paralelo

A versão paralela usa `ProcessPoolExecutor` e foi executada com as quantidades
de processos pedidas no enunciado.

| Processos | Execução 1 (s) | Execução 2 (s) | Execução 3 (s) | Média (s) |
|---:|---:|---:|---:|---:|
| 2 | 1,226917 | 1,396258 | 1,317296 | 1,313490 |
| 4 | 0,714750 | 0,790601 | 0,765779 | 0,757043 |
| 8 | 0,826022 | 0,842207 | 0,836305 | 0,834845 |

O programa comparou os resultados de todas essas execuções com o resultado
sequencial e não encontrou diferença.

## Etapa 3 – Registro dos resultados

Os cálculos usam `Speedup = T1 / Tp` e `Eficiência = Speedup / N`, sempre a
partir dos tempos médios.

| Número de processos | Tempo de execução (s) | Speedup | Eficiência |
|---:|---:|---:|---:|
| 1 | 1,884752 | 1,000 | 100,0% |
| 2 | 1,313490 | 1,435 | 71,7% |
| 4 | 0,757043 | 2,490 | 62,2% |
| 8 | 0,834845 | 2,258 | 28,2% |

Exemplo de conferência para 4 processos:
`1,884752 / 0,757043 = 2,490` e `2,490 / 4 = 0,622`, ou 62,2%.

## Etapa 4 – Análise dos resultados

### 1. O speedup foi igual ao número de processos?

Não. Com 2, 4 e 8 processos, os speedups foram 1,435, 2,490 e 2,258. Parte do
tempo é gasta com a infraestrutura do paralelismo, então nem todo o tempo pode
ser convertido em processamento útil simultâneo.

### 2. A eficiência permaneceu próxima de 100%?

Não. Ela foi 71,7% com 2 processos, 62,2% com 4 e 28,2% com 8. A queda mostra
que cada processo adicional foi menos aproveitado, principalmente quando foram
usados todos os 8 processadores lógicos da máquina.

### 3. O que aconteceu com o tempo ao aumentar os processos?

O tempo caiu de 1,884752 s para 1,313490 s com 2 processos e para 0,757043 s
com 4. Ao passar para 8 processos, porém, subiu para 0,834845 s. Portanto, o
menor tempo não ocorreu com a maior quantidade de processos.

### 4. Em algum momento o ganho começou a diminuir?

Sim. A partir de 4 processos o ganho não apenas diminuiu, mas houve uma pequena
regressão: 8 processos demoraram 0,077802 s a mais e o speedup caiu de 2,490
para 2,258.

### 5. Quais fontes de overhead estão presentes?

Há custo para criar e finalizar o pool a cada medição, serializar dados,
enviar tarefas aos processos, receber os resultados e montar a lista final. O
sistema operacional ainda precisa escalonar os processos e pode fazer trocas de
contexto. Com muitos processos, também pode ocorrer maior disputa pelos núcleos,
memória e cache.

## Etapa 5 – Experimento de granularidade

### Tempos individuais

| Tarefas | Processos | Execução 1 (s) | Execução 2 (s) | Execução 3 (s) | Média (s) |
|---:|---:|---:|---:|---:|---:|
| 20 | 1 | 0,409661 | 0,402074 | 0,397778 | 0,403171 |
| 20 | 2 | 0,315970 | 0,321156 | 0,316684 | 0,317937 |
| 20 | 4 | 0,287137 | 0,231544 | 0,246280 | 0,254987 |
| 20 | 8 | 0,384313 | 0,417462 | 0,349638 | 0,383805 |
| 100 | 1 | 1,957999 | 1,866789 | 1,880586 | 1,901791 |
| 100 | 2 | 1,098804 | 1,140570 | 1,121334 | 1,120236 |
| 100 | 4 | 0,822182 | 0,846817 | 0,795880 | 0,821627 |
| 100 | 8 | 0,794214 | 0,808219 | 0,808822 | 0,803752 |
| 500 | 1 | 9,694806 | 9,773301 | 9,547409 | 9,671839 |
| 500 | 2 | 5,036821 | 5,199074 | 5,101570 | 5,112488 |
| 500 | 4 | 3,546120 | 3,326026 | 3,356728 | 3,409625 |
| 500 | 8 | 3,204903 | 3,298999 | 3,236036 | 3,246646 |

### Comparação

| Tarefas | Processos | Tempo médio (s) | Speedup | Eficiência |
|---:|---:|---:|---:|---:|
| 20 | 2 | 0,317937 | 1,268 | 63,4% |
| 20 | 4 | 0,254987 | 1,581 | 39,5% |
| 20 | 8 | 0,383805 | 1,050 | 13,1% |
| 100 | 2 | 1,120236 | 1,698 | 84,9% |
| 100 | 4 | 0,821627 | 2,315 | 57,9% |
| 100 | 8 | 0,803752 | 2,366 | 29,6% |
| 500 | 2 | 5,112488 | 1,892 | 94,6% |
| 500 | 4 | 3,409625 | 2,837 | 70,9% |
| 500 | 8 | 3,246646 | 2,979 | 37,2% |

### 1. Como a quantidade de tarefas influencia o aproveitamento dos processos?

Mais tarefas mantiveram os processos ocupados por mais tempo e diluíram o custo
fixo do pool. Com 8 processos, por exemplo, o speedup passou de 1,050 com 20
tarefas para 2,366 com 100 e 2,979 com 500 tarefas.

### 2. Tarefas muito pequenas podem prejudicar o desempenho? Por quê?

Sim. No conjunto de 20 tarefas, 8 processos tiveram eficiência de apenas 13,1%
e quase empataram com a execução sequencial. Quando há pouco trabalho útil, o
tempo de criar processos, enviar as entradas e recolher as saídas pesa muito
mais no tempo total.

### 3. O que ocorre quando gerenciar uma tarefa custa quase o mesmo que processá-la?

O ganho esperado é consumido pelo overhead. O speedup se aproxima de 1 e a
versão paralela pode até ficar mais lenta, pois passa a executar o cálculo e
também todo o trabalho de comunicação e escalonamento.

### 4. Como os resultados se relacionam com a granularidade?

O cálculo de cada item permaneceu igual, mas a carga total ficou mais grossa em
relação ao custo fixo do paralelismo quando aumentei a lista. Por isso, 500
tarefas aproveitaram melhor os processos. O teste de 20 tarefas representa uma
carga efetivamente fina para esse pool, na qual o overhead tem proporção maior.

## Etapa 6 – Balanceamento de carga

Nesta etapa, os múltiplos de 10 usaram limite de 1.500.000 iterações, enquanto
os demais usaram 300.000. Também foram feitas três medições por configuração.

| Processos | Execução 1 (s) | Execução 2 (s) | Execução 3 (s) | Média (s) | Speedup | Eficiência |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2,705156 | 2,619364 | 2,743476 | 2,689332 | 1,000 | 100,0% |
| 2 | 1,552248 | 1,596722 | 1,560799 | 1,569923 | 1,713 | 85,7% |
| 4 | 1,143975 | 1,216055 | 1,094755 | 1,151595 | 2,335 | 58,4% |
| 8 | 1,062113 | 1,094492 | 1,115380 | 1,090662 | 2,466 | 30,8% |

Em uma execução instrumentada com 4 processos, uma tarefa comum levou em média
0,026440 s e uma tarefa pesada levou 0,130454 s, ou 4,934 vezes mais. A
distribuição observada foi:

| Processo | Tarefas | Pesadas | Soma dos tempos das tarefas (s) | Final relativo (s) |
|---:|---:|---:|---:|---:|
| 1460 | 24 | 2 | 0,900500 | 0,903299 |
| 4588 | 29 | 2 | 0,888525 | 0,892944 |
| 14400 | 26 | 3 | 0,984562 | 0,991861 |
| 15008 | 21 | 3 | 0,910531 | 0,917925 |

Os identificadores dos processos são específicos desta execução e podem mudar
em uma nova rodada.

### 1. Todos os processos terminaram aproximadamente no mesmo momento?

Eles terminaram relativamente próximos, mas não juntos. O primeiro encerrou sua
carga em 0,892944 s e o último em 0,991861 s, diferença de aproximadamente
0,099 s. A diferença aparece porque as tarefas não têm o mesmo custo.

### 2. O balanceamento de carga foi adequado?

Foi razoável, mas não perfeito. O escalonamento dinâmico distribuiu quantidades
diferentes de tarefas para compensar o custo: um processo fez 29 tarefas, e
outro fez 21. Mesmo assim, a soma dos tempos úteis variou de 0,888525 s a
0,984562 s e ainda houve uma cauda no final.

### 3. Alguns processos podem ficar ociosos enquanto outros executam?

Sim. Depois que a fila acaba, o processo que terminou em 0,892944 s não tinha
mais tarefa para buscar, enquanto outro continuou até 0,991861 s. Esse tempo de
espera afeta o tempo total da etapa paralela.

### 4. Como uma distribuição dinâmica pode melhorar o balanceamento?

Em vez de atribuir antecipadamente um bloco fixo a cada processo, uma fila
dinâmica entrega a próxima entrada ao processo que ficar livre. Foi usado
`chunksize=1`, então esse comportamento já ajudou a misturar tarefas comuns e
pesadas. Ele reduz o desequilíbrio, embora não elimine a espera causada pelas
últimas tarefas pesadas.

### 5. Dividir o trabalho em tarefas menores ajudaria? E o overhead?

Poderia ajudar porque uma tarefa pesada seria repartida entre mais processos,
diminuindo a cauda no final. Em troca, haveria mais itens para serializar,
agendar e recolher. Se a divisão for exagerada, o novo overhead pode superar o
ganho de balanceamento.

## Análise integrada

Os experimentos confirmam que mais processadores não produzem ganho
proporcional. No teste principal, 4 processos deram speedup de 2,490 e
eficiência de 62,2%; com 8, o speedup caiu para 2,258 e a eficiência para 28,2%.
Isso mostra o efeito do overhead de criação, comunicação, coleta e escalonamento.

A granularidade também foi importante. Com apenas 20 tarefas, 8 processos
tiveram speedup de 1,050, enquanto com 500 tarefas chegaram a 2,979, pois uma
carga maior amortizou o custo fixo e manteve mais processos ocupados. Na carga
desigual, as tarefas pesadas custaram 4,934 vezes mais e causaram cerca de
0,099 s de diferença entre o primeiro e o último processo a terminar, mostrando
que o balanceamento influencia o tempo final.

Pela Lei de Amdahl, a parte serial e os custos que não se beneficiam do
paralelismo limitam o speedup máximo. À medida que se adicionam processos, a
parte paralela diminui, mas criação do pool, comunicação, gerenciamento e
eventuais esperas continuam existindo. Por isso, depois de certo ponto, cada
processo extra contribui menos e pode até piorar o desempenho, como ocorreu de 4
para 8 processos no experimento principal.
