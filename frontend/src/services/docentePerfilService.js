import api from "./api";


export async function obtenerPerfilDocente(
  idCiclo = null
) {
  const params = {};

  if (idCiclo) {
    params.id_ciclo =
      idCiclo;
  }

  const response =
    await api.get(
      "/docente/perfil",
      {
        params
      }
    );

  return response.data;
}


export async function actualizarPerfilDocente(
  datos
) {
  const response =
    await api.put(
      "/docente/perfil",
      datos
    );

  return response.data;
}


export async function cambiarFotoPerfilDocente(
  archivo
) {
  const formData =
    new FormData();

  formData.append(
    "foto",
    archivo
  );

  const response =
    await api.post(
      "/docente/perfil/foto",
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


export async function obtenerFotoPerfilDocente() {
  return await api.get(
    "/docente/perfil/foto",
    {
      responseType: "blob"
    }
  );
}