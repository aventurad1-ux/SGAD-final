import api from "./api";

export async function login(correo, password) {
  const response = await api.post("/auth/login", {
    correo,
    password
  });

  return response.data;
}

export async function obtenerPerfil() {
  const response = await api.get("/auth/me");
  return response.data;
}

export async function renovarToken(refreshToken) {
  const response = await api.post(
    "/auth/refresh",
    {},
    {
      headers: {
        Authorization: `Bearer ${refreshToken}`
      }
    }
  );

  return response.data;
}

export async function logout(refreshToken) {
  const response = await api.post(
    "/auth/logout",
    {},
    {
      headers: {
        Authorization: `Bearer ${refreshToken}`
      }
    }
  );

  return response.data;
}