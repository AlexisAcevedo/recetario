# ADR-001: bcrypt vs Argon2 para Hashing de Contraseñas

## Estado
✅ Aceptado

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
2. **Amplio soporte**: `passlib` lo soporta nativamente con excelente API
3. **Facilidad de migración**: Si decidimos cambiar a Argon2, `passlib` permite migración gradual
4. **Performance predecible**: Work factor configurable (12 rounds default)
5. **Compatibilidad**: Funciona en todos los entornos sin dependencias adicionales

## Consecuencias

### Positivas
- API simple con `passlib[bcrypt]`
- Verificación automática de hashes antiguos
- Work factor ajustable según hardware

### Negativas
- Argon2 es teóricamente más seguro contra ataques GPU
- Límite de 72 bytes en contraseña (mitigado con pre-hashing)

### Mitigaciones
- Si Argon2 se vuelve necesario, `passlib` permite migración transparente
- Pre-hashing con SHA-256 elimina límite de 72 bytes

## Referencias
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [passlib Documentation](https://passlib.readthedocs.io/)
