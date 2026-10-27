import api from "./api";


export async function obtenerSolicitudesDocente(idCiclo = null) {
  const params = {};

  if (idCiclo) {
    params.id_ciclo = idCiclo;
  }

  const response = await api.get(
    "/docente/solicitudes",
    {
      params,
    }
  );

  return response.data;
}


export async function obtenerSolicitudDocente(idDestinatario) {
  const response = await api.get(
    `/docente/solicitudes/${idDestinatario}`
  );

  return response.data;
}


export async function realizarEntregaDocente(
  idDestinatario,
  idRequisito,
  archivo,
  observaciones = ""
) {
  const formData = new FormData();

  formData.append(
    "archivo",
    archivo
  );

  formData.append(
    "observaciones",
    observaciones
  );

  const response = await api.post(
    `/docente/solicitudes/${idDestinatario}/requisitos/${idRequisito}/entregar`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
}


export async function verArchivoEntrega(idVersion) {
  return await api.get(
    `/docente/solicitudes/versiones/${idVersion}/ver`,
    {
      responseType: "blob",
    }
  );
}


export async function descargarArchivoEntrega(idVersion) {
  return await api.get(
    `/docente/solicitudes/versiones/${idVersion}/descargar`,
    {
      responseType: "blob",
    }
  );
}