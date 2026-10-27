import api from "./api";


export async function obtenerDocumentosDocente() {
  const response = await api.get(
    "/docente/documentos"
  );

  return response.data;
}


export async function obtenerDetalleDocumentoDocente(
  idEntrega
) {
  const response = await api.get(
    `/docente/documentos/${idEntrega}`
  );

  return response.data;
}


export async function verArchivoDocumentoDocente(
  idVersion
) {
  return await api.get(
    `/docente/documentos/versiones/${idVersion}/ver`,
    {
      responseType: "blob",
    }
  );
}


export async function descargarArchivoDocumentoDocente(
  idVersion
) {
  return await api.get(
    `/docente/documentos/versiones/${idVersion}/descargar`,
    {
      responseType: "blob",
    }
  );
}