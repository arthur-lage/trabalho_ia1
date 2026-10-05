# Declaração de uso de Inteligência Artificial

Preencha esta seção para toda ferramenta de IA generativa utilizada durante o trabalho.

| Ferramenta | Finalidade | Arquivos/partes afetadas | Como o resultado foi verificado |
|---|---|---|---|
| Gemini | Explicar erros da implementação dos algoritmos | src/search.py | Revisão manual pelos autores, com testes manuais e correção de erros |
| Gemini | Explicar erros da implementação dos casos de testes | tests/test_search.py | Revisão manual pelos autores, com testes manuais e correção de erros |
| Codex (OpenAI, GPT-6) | Revisar o A*, aplicar a correção de `g` explicitamente armazenado conforme o diagnóstico fornecido, e auxiliar na escrita dos experimentos e testes de regressão | src/search.py, tests/test_search.py| Testes com `python -m unittest discover -s tests -v`; revisão manual pelos autores.
## Declaração

Declaramos que as implementações dos algoritmos de busca solicitados foram desenvolvidas pela equipe e que todo uso de ferramentas externas ou de IA foi registrado acima.
