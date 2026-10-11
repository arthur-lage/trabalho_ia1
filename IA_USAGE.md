# Declaração de uso de Inteligência Artificial

Preencha esta seção para toda ferramenta de IA generativa utilizada durante o trabalho.

| Ferramenta | Finalidade | Arquivos/partes afetadas | Como o resultado foi verificado |
|---|---|---|---|
| Gemini | Explicar erros da implementação dos algoritmos | src/search.py | Revisão manual pelos autores, com testes manuais e correção de erros |
| Gemini | Explicar erros da implementação dos casos de testes | tests/test_search.py | Revisão manual pelos autores, com testes manuais e correção de erros |
| Codex (OpenAI, GPT-6) | Revisar o A*, aplicar a correção de `g` explicitamente armazenado conforme o diagnóstico fornecido e auxiliar na escrita dos testes e do script de experimentos da Parte 1 | src/search.py, tests/test_search.py, scripts/run_experiments.py, README.md, requirements.txt, results/ | Testes com `python -m unittest discover -s tests -v`; comparação de A* com UCS em 200 mapas aleatórios com semente fixa e no mapa público; revisão dos resultados. |
| Codex (OpenAI, GPT-6) | Auxílio na criação dos testes de aceitação da Parte 2 e agregar os experimentos das 8 Rainhas sem implementar os algoritmos | tests/test_eight_queens.py, tests/test_hill_climbing.py | Revisado contra as seções 3.1–3.3 do PDF. |
## Declaração

Declaramos que as implementações dos algoritmos de busca solicitados foram desenvolvidas pela equipe e que todo uso de ferramentas externas ou de IA foi registrado acima.
