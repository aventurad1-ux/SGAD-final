import api from "./api";


export async function obtenerBitacora(
  filtros = {}
) {
  const response = await api.get(
    "/bitacora",
    {
      params: filtros
    }
  );

  return response.data;
}


export async function obtenerUsuariosBitacora() {
  const response = await api.get(
    "/bitacora/usuarios"
  );

  return response.data;
}


export default {
  obtenerBitacora,
  obtenerUsuariosBitacora
};