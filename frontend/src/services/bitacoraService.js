import api from "./api";

// Consultar registros de Bitácora
export const obtenerBitacora = async (filtros = {}) => {
  const response = await api.get("/bitacora", {
    params: filtros,
  });

  return response.data;
};

export default {
  obtenerBitacora,
};
