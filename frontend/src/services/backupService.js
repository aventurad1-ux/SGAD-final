import api from "./api";


export async function obtenerRespaldos() {
  const response = await api.get(
    "/directora/respaldos"
  );

  return response.data;
}


export async function generarRespaldo() {
  const response = await api.post(
    "/directora/respaldos"
  );

  return response.data;
}


export async function descargarRespaldo(
  nombre
) {
  const response = await api.get(
    `/directora/respaldos/${encodeURIComponent(nombre)}/descargar`,
    {
      responseType: "blob"
    }
  );

  const url = window.URL.createObjectURL(
    new Blob([response.data])
  );

  const enlace =
    document.createElement("a");

  enlace.href = url;
  enlace.download = nombre;

  document.body.appendChild(enlace);

  enlace.click();

  enlace.remove();

  window.URL.revokeObjectURL(url);
}