from typing import Any

from src.db.dal import DAL

ROLES_VALIDOS = ("socio", "cajero")


class CatalogosModule:
    def __init__(self, dal: DAL):
        self.dal = dal

    def listar_pymes(self) -> list[dict[str, Any]]:
        return self.dal.listar_pymes(solo_activas=False)

    def crear_pyme(self, nombre: str, activa: bool) -> int:
        nombre = nombre.strip()
        if not nombre:
            raise ValueError("El nombre no puede estar vacío.")
        return self.dal.crear_pyme(nombre, int(activa))

    def actualizar_pyme(self, pyme_id: int, nombre: str, activa: bool) -> bool:
        nombre = nombre.strip()
        if not nombre:
            raise ValueError("El nombre no puede estar vacío.")
        return self.dal.actualizar_pyme(pyme_id, nombre, int(activa))

    def eliminar_pyme(self, pyme_id: int) -> bool:
        # FK con ventas/paquetes puede levantar IntegrityError; la vista lo traduce a "desactivá".
        return self.dal.eliminar_pyme(pyme_id)

    def listar_personal(self) -> list[dict[str, Any]]:
        return self.dal.listar_personal(solo_activos=False)

    def crear_personal(self, nombre_display: str, rol: str, activo: bool) -> int:
        nombre_display = nombre_display.strip()
        if not nombre_display:
            raise ValueError("El nombre no puede estar vacío.")
        if rol not in ROLES_VALIDOS:
            raise ValueError(f"Rol inválido: {rol!r}. Debe ser uno de {ROLES_VALIDOS}.")
        return self.dal.crear_personal(nombre_display, rol, int(activo))

    def actualizar_personal(
        self,
        personal_id: int,
        nombre_display: str,
        rol: str,
        activo: bool,
    ) -> bool:
        nombre_display = nombre_display.strip()
        if not nombre_display:
            raise ValueError("El nombre no puede estar vacío.")
        if rol not in ROLES_VALIDOS:
            raise ValueError(f"Rol inválido: {rol!r}. Debe ser uno de {ROLES_VALIDOS}.")
        return self.dal.actualizar_personal(personal_id, nombre_display, rol, int(activo))

    def eliminar_personal(self, personal_id: int) -> bool:
        return self.dal.eliminar_personal(personal_id)
