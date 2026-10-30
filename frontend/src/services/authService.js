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


export async function preparar2FA(desafio) {
  const respuesta = await api.post("/auth/2fa/setup", {
    desafio
  });
  return respuesta.data;
}

export async function activar2FA(desafio, codigo) {
  const respuesta = await api.post("/auth/2fa/activate", {
    desafio,
    codigo
  });
  return respuesta.data;
}

export async function verificar2FA(desafio, codigo) {
  const respuesta = await api.post("/auth/2fa/verify", {
    desafio,
    codigo
  });
  return respuesta.data;
}


export async function recuperarAcceso2FA(desafio, codigo) {
  const respuesta = await api.post("/auth/2fa/recovery", {
    desafio,
    codigo
  });

  return respuesta.data;
}
