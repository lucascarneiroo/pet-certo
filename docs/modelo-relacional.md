# Modelo Relacional — Pet Certo (PostgreSQL)

Este é o modelo relacional (tabelas, chaves e tipos) exatamente como
implementado em `backend/database/schema.sql`. Modelagem original de
Henrique (Banco de Dados e Documentação); o schema completo (DDL) é o
próprio arquivo `schema.sql`, então aqui só resumimos.

| Tabela | Chave primária | Chaves estrangeiras | Observação |
|---|---|---|---|
| Usuario | idUsuario | — | tabela-pai; login é UNIQUE |
| Adotante | idUsuario | idUsuario → Usuario | cpf UNIQUE |
| Instituicao | idUsuario | idUsuario → Usuario | cnpj UNIQUE |
| Administrador | idUsuario | idUsuario → Usuario | — |
| RegistroAdministrativo | idRegistroAdmin | idAdministrador → Administrador | log de ações administrativas |
| Animal | idAnimal | idInstituicao → Instituicao | status: Disponível / Em Processo / Adotado |
| CaracteristicaAnimal | idCaracteristica | — | nome UNIQUE; vocabulário fixo (ver tags_padrao.py) |
| AnimalCaracteristica | (idAnimal, idCaracteristica) | idAnimal → Animal, idCaracteristica → CaracteristicaAnimal | tabela associativa N:N |
| Favorito | idFavorito | idAdotante → Adotante, idAnimal → Animal | UNIQUE(idAdotante, idAnimal) |
| Recomendacao | idRecomendacao | idAdotante → Adotante, idAnimal → Animal | gerada pelo algoritmo de compatibilidade |
| Compatibilidade | idCompatibilidade | idAdotante → Adotante, idAnimal → Animal | score 0-100, fatores em JSONB |
| ManifestacaoInteresse | idManifestacao | idAdotante → Adotante, idAnimal → Animal | status: Pendente / Aprovada / Recusada |
| ProcessoAdocao | idProcesso | idManifestacao → ManifestacaoInteresse (UNIQUE) | 1:1 com a manifestação aprovada |
| EtapaAdocao | idEtapa | idProcesso → ProcessoAdocao | uma linha por etapa (Análise, Visita, Documentação, Aprovação) |
| HorarioVisita | idHorario | idInstituicao → Instituicao | slot oferecido pela instituição |
| Visita | idVisita | idProcesso → ProcessoAdocao, idHorario → HorarioVisita (UNIQUE) | agendamento efetivo |
| Documento | idDocumento | idProcesso → ProcessoAdocao | arquivos anexados ao processo |
| HistoricoProcesso | idHistorico | idProcesso → ProcessoAdocao | auditoria de cada mudança do processo |

## Regras de integridade aplicadas em código (Python), além do banco

- Só é possível manifestar interesse em animal com status `Disponível`.
- Aprovar uma manifestação cria o `ProcessoAdocao` e as 4 `EtapaAdocao`
  (a primeira `Em Andamento`, as demais `Pendente`), e muda o animal para
  `Em Processo`.
- Concluir o processo muda o animal para `Adotado`; cancelar devolve o
  animal para `Disponível` somente se não houver outro processo em
  andamento para o mesmo animal.
- Uma instituição só pode gerenciar (aprovar/recusar manifestação, avançar
  etapa, agendar visita, concluir/cancelar processo) os processos dos
  animais que ela mesma cadastrou (`Animal.idInstituicao == usuario.id`).
- Etiquetas de `AnimalCaracteristica` são restritas ao vocabulário padrão
  definido em código — o banco aceitaria qualquer texto, mas a API rejeita
  etiquetas fora da lista para manter o algoritmo de compatibilidade
  funcionando de forma previsível.
