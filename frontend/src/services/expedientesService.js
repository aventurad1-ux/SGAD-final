import api from "./api";


export async function obtenerExpedientes(idCiclo = null) {
  const config = {};

  if (idCiclo) {
    config.params = {
      id_ciclo: idCiclo
    };
  }

  const response = await api.get(
    "/directora/expedientes",
    config
  );

  return response.data;
}


export async function obtenerCatalogosExpedientes(
  idCiclo
) {
  const response = await api.get(
    "/directora/expedientes/catalogos",
    {
      params: {
        id_ciclo: idCiclo
      }
    }
  );

  return response.data;
}


export async function crearMatricula(datos) {
  const response = await api.post(
    "/directora/expedientes/matriculas",
    datos
  );

  return response.data;
}


export async function obtenerDetalleExpediente(
  idEstudiante,
  idCiclo
) {
  const response = await api.get(
    `/directora/expedientes/estudiantes/${idEstudiante}`,
    {
      params: {
        id_ciclo: idCiclo
      }
    }
  );

  return response.data;
}


export async function subirDocumento(
  idEstudiante,
  datos
) {
  const formData = new FormData();

  formData.append(
    "id_ciclo",
    datos.id_ciclo
  );

  formData.append(
    "id_requisito",
    datos.id_requisito
  );

  formData.append(
    "observaciones",
    datos.observaciones || ""
  );

  formData.append(
    "archivo",
    datos.archivo
  );

  const response = await api.post(
    `/directora/expedientes/estudiantes/${idEstudiante}/documentos`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    }
  );

  return response.data;
}


export async function obtenerVersionesDocumento(
  idDocumento
) {
  const response = await api.get(
    `/directora/expedientes/documentos/${idDocumento}/versiones`
  );

  return response.data;
}


export async function descargarDocumento(
  idDocumento
) {
  const response = await api.get(
    `/directora/expedientes/documentos/${idDocumento}/descargar`,
    {
      responseType: "blob"
    }
  );

  const disposition =
    response.headers["content-disposition"];

  let nombreArchivo =
    "documento";

  if (disposition) {
    const match = disposition.match(
      /filename="?([^"]+)"?/
    );

    if (match?.[1]) {
      nombreArchivo = match[1];
    }
  }

  const url = URL.createObjectURL(
    response.data
  );

  const enlace =
    document.createElement("a");

  enlace.href = url;
  enlace.download = nombreArchivo;

  document.body.appendChild(enlace);

  enlace.click();
  enlace.remove();

  URL.revokeObjectURL(url);
}


export async function verDocumento(
  idDocumento
) {
  const response = await api.get(
    `/directora/expedientes/documentos/${idDocumento}/ver`,
    {
      responseType: "blob"
    }
  );

  const url = URL.createObjectURL(
    response.data
  );

  window.open(
    url,
    "_blank",
    "noopener,noreferrer"
  );

  setTimeout(() => {
    URL.revokeObjectURL(url);
  }, 60000);
}