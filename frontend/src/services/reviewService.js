import api from "./api";

export async function obtenerBandejaRevision() {
  const response = await api.get(
    "/directora/revision"
  );

  return response.data;
}

export async function aprobarEntrega(idEntrega) {
  const response = await api.post(
    `/directora/revision/${idEntrega}/aprobar`
  );

  return response.data;
}

export async function solicitarCorreccion(
  idEntrega,
  observaciones
) {
  const response = await api.post(
    `/directora/revision/${idEntrega}/correccion`,
    {
      observaciones
    }
  );

  return response.data;
}