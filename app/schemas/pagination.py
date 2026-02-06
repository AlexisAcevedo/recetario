"""
Esquema de Paginación Genérica.
"""
from typing import Generic, TypeVar, List
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    """
    Respuesta paginada genérica.
    
    Attributes:
        items: Lista de elementos de la página actual
        total: Total de elementos en la base de datos
        page: Número de página actual (1-based)
        per_page: Elementos por página
        total_pages: Total de páginas disponibles
    """
    items: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int
    
    model_config = ConfigDict(from_attributes=True)
