import api from "./api";


export async function obtenerUsuarios(idCiclo = null) {
  const config = {};

  if (idCiclo) {
    config.params = {
      id_ciclo: idCiclo
    };
  }

  const response = await api.get(
    "/directora/usuarios",
    config
  );

  return response.data;
}


export async function obtenerCatalogosUsuarios(
  idCiclo = null
) {
  const config = {};

  if (idCiclo) {
    config.params = {
      id_ciclo: idCiclo
    };
  }

  const response = await api.get(
    "/directora/usuarios/catalogos",
    config
  );

  return response.data;
}


export async function crearUsuario(datos) {
  const response = await api.post(
    "/directora/usuarios",
    datos
  );

  return response.data;
}


export async function actualizarUsuario(
  idUsuario,
  datos
) {
  const response = await api.put(
    `/directora/usuarios/${idUsuario}`,
    datos
  );

  return response.data;
}


export async function cambiarEstadoUsuario(
  idUsuario,
  activo
) {
  const response = await api.patch(
    `/directora/usuarios/${idUsuario}/estado`,
    {
      activo
    }
  );

  return response.data;
}