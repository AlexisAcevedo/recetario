# ADR-001: bcrypt vs Argon2 para Hashing de Contraseñas

## Estado
✅ Aceptado (actualizado: migrado de passlib a bcrypt directo)

## Contexto

Al implementar el sistema de autenticación, necesitábamos elegir un algoritmo de hashing para almacenar contraseñas de forma segura.

**Opciones evaluadas:**
1. **bcrypt** - Algoritmo probado desde 1999, amplio soporte
2. **Argon2** - Ganador de Password Hashing Competition 2015, más moderno
3. **scrypt** - Alternativa memory-hard
4. **PBKDF2** - Estándar NIST, pero más débil

## Decisión

**Elegimos bcrypt** por las siguientes razones:

1. **Madurez y estabilidad**: 25+ años de uso en producción
2. **Uso directo de bcrypt**: Sin wrapper (`passlib` eliminado por incompatibilidades con Python 3.14)
3. **Performance predecible**: Work factor configurable (12 rounds default)
4. **Compatibilidad**: Funciona en todos los entornos sin dependencias adicionales
5. **Control explícito**: Truncado a 72 bytes gestionado manualmente en `security.py`

## Consecuencias

### Positivas
- API directa con `bcrypt` sin wrappers intermedios
- Menos dependencias (eliminado `passlib`)
- Compatible con Python 3.14+
- Work factor ajustable según hardware

### Negativas
- Argon2 es teóricamente más seguro contra ataques GPU
- Límite de 72 bytes en contraseña (gestionado con truncado explícito en `app/core/security.py`)

### Mitigaciones
- Si Argon2 se vuelve necesario, la migración se puede hacer cambiando solo `security.py`

## Referencias
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [bcrypt PyPI](https://pypi.org/project/bcrypt/)
