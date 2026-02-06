# ADR-003: SQLAlchemy ORM vs Raw SQL

## Estado
✅ Aceptado

## Contexto

Al diseñar la capa de acceso a datos, debíamos elegir entre usar un ORM o queries SQL directos.

**Opciones evaluadas:**
1. **SQLAlchemy ORM** - Abstracción completa, mapeo de objetos
2. **SQLAlchemy Core** - SQL expresivo sin ORM completo
3. **Raw SQL con psycopg2** - Control total, más verbose
4. **Tortoise ORM** - Async-first, menos maduro

## Decisión

**Elegimos SQLAlchemy ORM 2.0** por las siguientes razones:

1. **Productividad**: Modelos declarativos, relaciones automáticas
2. **Type hints**: SQLAlchemy 2.0 tiene soporte nativo de tipos
3. **Flexibilidad**: Podemos usar queries raw cuando sea necesario
4. **Ecosistema**: Integración con Alembic, excelente documentación
5. **Comunidad**: Estándar de facto en Python

## Consecuencias

### Positivas
- Código más limpio y mantenible
- Migraciones automáticas con Alembic
- Protección contra SQL injection por defecto
- Relaciones lazy/eager configurables

### Negativas
- Overhead de abstracción (mitigable)
- Queries N+1 si no se configura bien
- Curva de aprendizaje

### Mitigaciones
- Usar `joinedload()` para eager loading donde sea necesario
- Monitorear queries con logging SQL
- Para queries críticas, usar `text()` con SQL raw

## Ejemplo

```python
# ORM declarativo
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    sessions = relationship("Session", back_populates="user")

# Query con eager loading
users = db.query(User).options(joinedload(User.sessions)).all()
```

## Referencias
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
