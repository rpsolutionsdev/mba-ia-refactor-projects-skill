# Template de Relatório de Auditoria Arquitetural

Este template define o formato oficial e obrigatório para o relatório de auditoria gerado na **Fase 2** da skill `/refactor-arch`.

---

```markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome-do-projeto>
Stack:   <Linguagem> + <Framework>
Files:   <quantidade> analyzed | ~<linhas> lines of code

## Summary
CRITICAL: <qtd> | HIGH: <qtd> | MEDIUM: <qtd> | LOW: <qtd>

## Findings

### [<SEVERIDADE>] <Nome do Anti-Pattern ou Code Smell>
File: <caminho_do_arquivo>:<linha_inicio>-<linha_fim>
Description: <Descrição técnica clara e concisa do problema encontrado.>
Impact: <Impacto na arquitetura, segurança, manutenibilidade ou performance.>
Recommendation: <Ação corretiva recomendada para a refatoração MVC.>

### [<SEVERIDADE>] <Nome do Anti-Pattern ou Code Smell>
File: <caminho_do_arquivo>:<linha>
Description: <Descrição técnica do problema.>
Impact: <Impacto do problema.>
Recommendation: <Recomendação de correção.>

[... repetir para todos os findings encontrados ...]

================================
Total: <total_findings> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## ⚠️ Regras Obrigatórias de Formatação

1. **Ordenação Decrescente**: Os findings **DEVEM** ser listados rigorosamente na ordem:
   - 🔴 `CRITICAL` primeiro
   - 🟠 `HIGH` em segundo
   - 🟡 `MEDIUM` em terceiro
   - 🟢 `LOW` por último
2. **Localização Exata**: O campo `File:` deve conter o caminho relativo do arquivo com a linha ou intervalo de linhas (`arquivo.ext:10-25` ou `arquivo.ext:42`).
3. **Mínimo de Findings**: O relatório deve listar no mínimo 5 findings válidos e relevantes.
4. **Pausa para Confirmação**: O rodapé deve incluir a pergunta interativa `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` antes de qualquer alteração de código.
