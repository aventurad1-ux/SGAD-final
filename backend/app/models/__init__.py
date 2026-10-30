
from app.models.associations import rol_permisos
from app.models.role import Role
from app.models.permiso import Permiso
from app.models.usuario import Usuario
from app.models.usuario_permiso import UsuarioPermiso
from app.models.refresh_token import RefreshToken

from .ciclo_escolar import CicloEscolar
from .solicitud import Solicitud
from .solicitud_destinatario import SolicitudDestinatario
from .solicitud_requisito import SolicitudRequisito
from .entrega import Entrega
from .version_entrega import VersionEntrega
from .revision_entrega import RevisionEntrega
from .seccion import Seccion
from .estudiante import Estudiante
from .matricula import Matricula
from .requisito_expediente import RequisitoExpediente
from .documento_estudiante import DocumentoEstudiante
from .version_documento_estudiante import VersionDocumentoEstudiante
from .categoria_repositorio import CategoriaRepositorio
from .documento_institucional import DocumentoInstitucional
from .version_documento_institucional import VersionDocumentoInstitucional
from .notificacion import Notificacion

# NUEVO: Modelo del historial de respaldos
from .respaldo import Respaldo
from .bitacora import Bitacora


__all__ = [
    "rol_permisos",
    "Role",
    "Permiso",
    "Usuario",
    "UsuarioPermiso",
    "RefreshToken",
    "CicloEscolar",
    "Solicitud",
    "SolicitudDestinatario",
    "SolicitudRequisito",
    "Entrega",
    "VersionEntrega",
    "RevisionEntrega",
    "Seccion",
    "Estudiante",
    "Matricula",
    "RequisitoExpediente",
    "DocumentoEstudiante",
    "VersionDocumentoEstudiante",
    "CategoriaRepositorio",
    "DocumentoInstitucional",
    "VersionDocumentoInstitucional",
    "Notificacion",
    "Respaldo",
    "Bitacora",
]

from app.models.usuario_2fa import Usuario2FA

from app.models.usuario_2fa import Usuario2FA

from app.models.codigo_recuperacion_2fa import CodigoRecuperacion2FA

from app.models.desafio_2fa_consumido import Desafio2FAConsumido