# Global Solution 2 - Pensamento Computacional e Automação com Python 
## Citizen Assist AI - Orientação sobre Documentação

**Integrantes:**
* Caio Marinho Pereira - RM: 572873

---

## Público e Problema
**Público:** pessoas que precisam resolver questões de documentação e não sabem por onde começar (cartórios, Poupatempo, Polícia Federal, consulados, Justiça Eleitoral, etc).

**Problema:** a informação existe, mas está espalhada e misturada com sites que parecem oficiais, mas não são. A solução, Citizen Assist AI, responde em linguagem simples, somente com o que está na base de conhecimento, mostrando documentos necessáris, onde ir, fonte oficial das informações e data de verificação, sem coletar dados pessoais e sem redirecionar o usuário automaticamente.

## ODS (Objetivos de Desenvolvimento Sustentável) relacionados
- **ODS 10** → **Redução das Desigualdades**: Quem tem menos acesso a informações perde mais tempo e dinheiro com burocracias. 
- **ODS 16** → **Paz, Justiça e Instituições Eficazes**: acesso à informação e serviços públicos mais transparentes

## Como executar
Requer apenas Python 3.8+.
```bash
python main.py
```

## Estrutura
```
GS2_PCAP/
├── main.py
├── base_conhecimento.py
├── assistente.py
├── orientacao.py
├── testes.py
└── data/
    ├── base_conhecimento.json
    ├── historico.json      # gerado
    └── atendimentos.csv    # gerado
```

## Regra de pontuação
A pergunta é normalizada (minúsculas, sem acentos e sem pontuações) e comparada com cada orientação:

| Regra | Pontos |
|---|:---:|
| Palavra-chave da orientação aparece na pergunta | +3 |
| Palavra da pergunta aparece no título | +1 |

| Melhor pontuação | Resultado |
|---|---|
| 6 ou mais | Confiança **ALTA** |
| 3 a 5 | Confiança **MÉDIA** |
| Menos de 3 | "Não encontrei" e sugere outras palavras e categorias |

`buscar()` devolve uma lista de tuplas `(pontos, orientacao)` da maior para a menor pontuação. O assistente mostra a melhor orientação e até 2 alternativas com confiança mínima.

**Exemplo real:** "Como tiro a segunda via do RG?" → orientação 1: `rg` (+3) + `segunda via do rg` (+3) + "segunda" no título (+1) = **7 pontos, ALTA**.

**Dados pessoais:** pergunta com 8 ou mais dígitos, ou com `@`, é recusada e não é registrada.

**Indicadores:** "Taxa de acerto" e "Resposta encontrada" são calculados sobre o total de atendimentos. "Tempo médio" considera só os atendimentos em que houve resposta. Um atendimento começa na primeira pergunta válida e termina ao encontrar a resposta, ou quando a pessoa digita 0 (desistência, registrada como não resolvida).

## Fontes consultadas
Cada orientação do JSON indica sua fonte oficial. Entre elas: 
- portal gov.br
- Receita Federal
- Polícia Federal
- TSE
- INSS

## Teste com usuários
- Pessoas testadas (quantidade):
- Indicadores obtidos:
- Dúvidas sem solução:
- Melhorias feitas a partir do teste: 

## Limitações
- A busca é por regras. Não entende sentido, só palavras. Erros de digitação não combinam, e só funcionaria se existisse uma palavra-chave com a grafia errada. 
- Responde apenas o que está na base. Como informações oficiais mudam ao decorrer do tempo, as informações eventualmente precisarão ser reconferidas. 
- Os procedimentos variam por estado e município. O assistente orienta de forma geral.
- Não é um canal oficial e não substitui o atendimento do órgão responsável. 

## Vídeo técnico
(link)