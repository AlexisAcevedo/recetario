# Architecture Decision Records (ADR)

Este directorio contiene los registros de decisiones arquitectónicas del proyecto Recetario API.

## ¿Qué es un ADR?

Un ADR documenta una decisión arquitectónica significativa junto con su contexto y consecuencias.

## Índice

| ADR | Título | Estado |
|-----|--------|--------|
| [001](001-bcrypt-vs-argon2.md) | bcrypt vs Argon2 para hashing | ✅ Aceptado |
| [002](002-refresh-tokens-strategy.md) | Estrategia de Refresh Tokens | ✅ Aceptado |
| [003](003-sqlalchemy-orm.md) | SQLAlchemy ORM vs Raw SQL | ✅ Aceptado |

## Template

```markdown
# ADR-XXX: Título

## Estado
[Propuesto | Aceptado | Deprecado | Reemplazado]

## Contexto
[Descripción del problema o situación]

## Decisión
[La decisión tomada]

## Consecuencias
### Positivas
- ...

### Negativas
- ...
```
