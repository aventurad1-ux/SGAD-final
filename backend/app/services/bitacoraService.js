
import api from "./api";

// Obtener registros de la bitácora con filtros y paginación
export const obtenerBitacora = async (filtros = {}) => {
  const response = await api.get("/bitacora", {
    params: filtros,
  });

  return response.data;
};

export default {
  obtenerBitacora,
};
