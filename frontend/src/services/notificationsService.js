import api from "./api";


export async function obtenerNotificaciones(
  idCiclo = null
) {
  const config = {};

  if (idCiclo) {
    config.params = {
      id_ciclo: idCiclo
    };
  }

  const response = await api.get(
    "/notificaciones",
    config
  );

  return response.data;
}


export async function marcarNotificacionLeida(
  idNotificacion
) {
  const response = await api.patch(
    `/notificaciones/${idNotificacion}/leer`
  );

  return response.data;
}


export async function marcarTodasNotificacionesLeidas(
  idCiclo = null
) {
  const config = {};

  if (idCiclo) {
    config.params = {
      id_ciclo: idCiclo
    };
  }

  const response = await api.patch(
    "/notificaciones/leer-todas",
    {},
    config
  );

  return response.data;
}