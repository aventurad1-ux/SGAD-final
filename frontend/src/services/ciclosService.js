import api from "./api";


export async function obtenerCiclos(idCiclo = null) {
  const config = {};

  if (idCiclo) {
    config.params = {
      id_ciclo: idCiclo
    };
  }

  const response = await api.get(
    "/directora/ciclos",
    config
  );

  return response.data;
}


export async function obtenerCatalogosCiclo() {
  const response = await api.get(
    "/directora/ciclos/catalogos"
  );

  return response.data;
}


export async function crearSeccion(datos) {
  const response = await api.post(
    "/directora/ciclos/secciones",
    datos
  );

  return response.data;
}


export async function actualizarResponsable(
  idSeccion,
  idDocente
) {
  const response = await api.put(
    `/directora/ciclos/secciones/${idSeccion}/responsable`,
    {
      id_docente: idDocente || null
    }
  );

  return response.data;
}


export async function cerrarCiclo(idCiclo) {
  const response = await api.post(
    `/directora/ciclos/${idCiclo}/cerrar`
  );

  return response.data;
}


export async function crearCiclo(datos) {
  const response = await api.post(
    "/directora/ciclos",
    datos
  );

  return response.data;
}