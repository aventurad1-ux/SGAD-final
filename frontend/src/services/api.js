import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:5000/api",
  headers: {
    "Content-Type": "application/json"
  }
});

api.interceptors.request.use((config) => {
  const accessToken = localStorage.getItem("access_token");

  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  return config;
});


api.interceptors.response.use(
  (response) => response,

  (error) => {
    const estado = error.response?.status;

    const token = localStorage.getItem(
      "access_token"
    );

    if (estado === 401 && token) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("usuario");
      localStorage.removeItem("sgad_ciclo");

      sessionStorage.removeItem(
        "sgad_desafio_2fa"
      );

      sessionStorage.removeItem(
        "sgad_2fa_setup"
      );

      if (
        window.location.pathname !== "/"
      ) {
        window.location.replace("/");
      }
    }

    return Promise.reject(error);
  }
);


export default api;