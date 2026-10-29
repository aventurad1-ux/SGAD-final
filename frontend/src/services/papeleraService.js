import api from "./api";


export async function obtenerPapelera(
  idCiclo = null
) {
  const params = {};

  if (idCiclo) {
    params.id_ciclo = idCiclo;
  }

  const response =
    await api.get(
      "/directora/papelera",
      {
        params
      }
    );

  return response.data;
}


export async function obtenerDetallePapelera(
  idDocumento
) {
  const response =
    await api.get(
      `/directora/papelera/repositorio/${idDocumento}`
    );

  return response.data;
}


export async function restaurarDocumentoPapelera(
  idDocumento
) {
  const response =
    await api.patch(
      `/directora/papelera/repositorio/${idDocumento}/restaurar`
    );

  return response.data;
}


export async function verDocumentoPapelera(
  idDocumento
) {
  const response =
    await api.get(
      `/directora/papelera/repositorio/${idDocumento}/ver`,
      {
        responseType: "blob"
      }
    );

  const tipo =
    response.headers["content-type"] ||
    "application/octet-stream";

  const blob =
    new Blob(
      [response.data],
      {
        type: tipo
      }
    );

  const url =
    URL.createObjectURL(
      blob
    );

  window.open(
    url,
    "_blank"
  );

  setTimeout(() => {
    URL.revokeObjectURL(
      url
    );
  }, 60000);
}


export async function descargarDocumentoPapelera(
  idDocumento
) {
  const response =
    await api.get(
      `/directora/papelera/repositorio/${idDocumento}/descargar`,
      {
        responseType: "blob"
      }
    );

  const disposition =
    response.headers[
      "content-disposition"
    ];

  let nombre =
    "documento";

  if (disposition) {
    const match =
      disposition.match(
        /filename\*?=(?:UTF-8''|")?([^";]+)/i
      );

    if (
      match &&
      match[1]
    ) {
      nombre =
        decodeURIComponent(
          match[1]
            .replace(/"/g, "")
        );
    }
  }

  const blob =
    new Blob(
      [response.data],
      {
        type:
          response.headers[
            "content-type"
          ] ||
          "application/octet-stream"
      }
    );

  const url =
    URL.createObjectURL(
      blob
    );

  const enlace =
    document.createElement(
      "a"
    );

  enlace.href =
    url;

  enlace.download =
    nombre;

  document.body.appendChild(
    enlace
  );

  enlace.click();

  enlace.remove();

  URL.revokeObjectURL(
    url
  );
}


export async function eliminarDocumentoPapelera(
  idDocumento
) {
  const response =
    await api.delete(
      `/directora/papelera/repositorio/${idDocumento}`
    );

  return response.data;
}