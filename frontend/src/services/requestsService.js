import api from "./api";

export async function obtenerSolicitudes(idCiclo = null) {
  const config = {};

  if (idCiclo) {
    config.params = {
      id_ciclo: idCiclo
    };
  }

  const response = await api.get(
    "/directora/solicitudes",
    config
  );

  return response.data;
}

export async function obtenerCatalogosSolicitudes() {
  const response = await api.get(
    "/directora/solicitudes/catalogos"
  );

  return response.data;
}

export async function crearSolicitud(datos) {
  const response = await api.post(
    "/directora/solicitudes",
    datos
  );

  return response.data;
}

export async function obtenerCumplimiento(idSolicitud) {
  const response = await api.get(
    `/directora/solicitudes/${idSolicitud}/cumplimiento`
  );

  return response.data;
}

export async function cerrarSolicitud(idSolicitud) {
  const response = await api.post(
    `/directora/solicitudes/${idSolicitud}/cerrar`
  );

  return response.data;
}

export async function reabrirSolicitud(
  idSolicitud,
  fechaLimite
) {
  const response = await api.post(
    `/directora/solicitudes/${idSolicitud}/reabrir`,
    {
      fecha_limite: fechaLimite
    }
  );

  return response.data;
}