<template>
  <div>
    <h1>Login SGAD</h1>

    <button @click="probarLogin">
      Probar login
    </button>

    <pre>{{ resultado }}</pre>
  </div>
</template>

<script>
import { login } from "../../services/authService";

export default {
  name: "LoginView",

  data() {
    return {
      resultado: ""
    };
  },

  methods: {
    async probarLogin() {
      try {
        const data = await login(
          "directora@sgad.demo",
          "Directora2026"
        );

        localStorage.setItem(
          "access_token",
          data.access_token
        );

        localStorage.setItem(
          "refresh_token",
          data.refresh_token
        );

        this.resultado = data;
      } catch (error) {
        this.resultado =
          error.response?.data || error.message;
      }
    }
  }
};
</script>