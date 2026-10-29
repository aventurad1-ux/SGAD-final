import api from "./api";


export async function obtenerDocumentosRepositorio(
  filtros = {}
) {
  const params = {};

  if (filtros.id_ciclo) {
    params.id_ciclo = filtros.id_ciclo;
  }

  if (filtros.buscar) {
    params.buscar = filtros.buscar;
  }

  if (filtros.id_categoria) {
    params.id_categoria =
      filtros.id_categoria;
  }

  if (filtros.estado) {
    params.estado = filtros.estado;
  }

  if (filtros.nivel_acceso) {
    params.nivel_acceso =
      filtros.nivel_acceso;
  }

  const response = await api.get(
    "/directora/repositorio",
    {
      params
    }
  );

  return response.data;
}


export async function obtenerCategoriasRepositorio() {
  const response = await api.get(
    "/directora/repositorio/categorias"
  );

  return response.data;
}


export async function crearCategoriaRepositorio(
  nombre
) {
  const response = await api.post(
    "/directora/repositorio/categorias",
    {
      nombre
    }
  );

  return response.data;
}


export async function cambiarEstadoCategoriaRepositorio(
  idCategoria,
  activa
) {
  const response = await api.patch(
    `/directora/repositorio/categorias/${idCategoria}/estado`,
    {
      activa
    }
  );

  return response.data;
}


export async function obtenerDetalleDocumentoRepositorio(
  idDocumento
) {
  const response = await api.get(
    `/directora/repositorio/${idDocumento}`
  );

  return response.data;
}


export async function subirDocumentoRepositorio(
  datos
) {
  const formData = new FormData();

  formData.append(
    "id_ciclo",
    datos.id_ciclo
  );

  formData.append(
    "id_categoria",
    datos.id_categoria
  );

  formData.append(
    "titulo",
    datos.titulo
  );

  formData.append(
    "descripcion",
    datos.descripcion || ""
  );

  formData.append(
    "nivel_acceso",
    datos.nivel_acceso
  );

  formData.append(
    "fecha_documental",
    datos.fecha_documental
  );

  formData.append(
    "archivo",
    datos.archivo
  );

  const response = await api.post(
    "/directora/repositorio",
    formData,
    {
      headers: {
        "Content-Type":
          "multipart/form-data"
      }
    }
  );

  return response.data;
}


export async function actualizarDocumentoRepositorio(
  idDocumento,
  datos
) {
  const response = await api.put(
    `/directora/repositorio/${idDocumento}`,
    datos
  );

  return response.data;
}


export async function reemplazarArchivoRepositorio(
  idDocumento,
  datos
) {
  const formData = new FormData();

  formData.append(
    "motivo",
    datos.motivo
  );

  formData.append(
    "archivo",
    datos.archivo
  );

  const response = await api.post(
    `/directora/repositorio/${idDocumento}/reemplazar`,
    formData,
    {
      headers: {
        "Content-Type":
          "multipart/form-data"
      }
    }
  );

  return response.data;
}


export async function enviarDocumentoPapelera(
  idDocumento
) {
  const response = await api.patch(
    `/directora/repositorio/${idDocumento}/papelera`
  );

  return response.data;
}


export async function verDocumentoRepositorio(
  idDocumento
) {
  const response = await api.get(
    `/directora/repositorio/${idDocumento}/ver`,
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


export async function descargarDocumentoRepositorio(
  idDocumento
) {
  const response = await api.get(
    `/directora/repositorio/${idDocumento}/descargar`,
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


export async function descargarVersionRepositorio(
  idVersion
) {
  const response = await api.get(
    `/directora/repositorio/versiones/${idVersion}/descargar`,
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