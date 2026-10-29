
import api from "./api";

// Obtener datos del perfil de la directora
export async function obtenerPerfilDirectora() {
  const response = await api.get("/directora/perfil");
  return response.data;
}

// Guardar los cambios del perfil
export async function actualizarPerfilDirectora(datos) {
  const response = await api.put(
    "/directora/perfil",
    datos
  );

  return response.data;
}

// Cambiar fotografía
export async function cambiarFotoPerfilDirectora(archivo) {
  const formData = new FormData();
  formData.append("foto", archivo);

  const response = await api.post(
    "/directora/perfil/foto",
    formData,
    {
      headers: {
        "Content-Type": undefined
      }
    }
  );

  return response.data;
}

// Consultar fotografía
export async function obtenerFotoPerfilDirectora() {
  const response = await api.get(
    "/directora/perfil/foto",
    {
      responseType: "blob"
    }
  );

  return response.data;
}

// Eliminar fotografía
export async function quitarFotoPerfilDirectora() {
  const response = await api.delete(
    "/directora/perfil/foto"
  );

  return response.data;
}
