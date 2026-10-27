import api from "./api";


export async function obtenerMisEstudiantes(
  idCiclo = null
) {
  const params = {};

  if (idCiclo) {
    params.id_ciclo = idCiclo;
  }

  const response = await api.get(
    "/docente/estudiantes",
    {
      params
    }
  );

  return response.data;
}


export async function obtenerMiEstudiante(
  idEstudiante,
  idCiclo
) {
  const response = await api.get(
    `/docente/estudiantes/${idEstudiante}`,
    {
      params: {
        id_ciclo: idCiclo
      }
    }
  );

  return response.data;
}


export async function verDocumentoDocente(
  idDocumento
) {
  const response = await api.get(
    `/docente/estudiantes/documentos/${idDocumento}/ver`,
    {
      responseType: "blob"
    }
  );

  return response;
}


export async function descargarDocumentoDocente(
  idDocumento
) {
  const response = await api.get(
    `/docente/estudiantes/documentos/${idDocumento}/descargar`,
    {
      responseType: "blob"
    }
  );

  return response;
}


export async function obtenerVersionesDocumentoDocente(
  idDocumento
) {
  const response = await api.get(
    `/docente/estudiantes/documentos/${idDocumento}/versiones`
  );

  return response.data;
}