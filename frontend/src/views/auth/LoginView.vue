<template>
  <main class="login-page">
    <section class="left-panel">
      <div class="school-info">
        <div class="logo-wrapper">
          <img
            src="../../assets/images/logo.jpeg"
            alt="Logo Escuela Orfelinda Osorio Lemus"
          />
        </div>

        <div class="school-text">
          <p class="school-type">
            ESCUELA OFICIAL RURAL MIXTA
          </p>

          <h1>
            Orfelinda
            <br />
            Osorio Lemus
          </h1>

          <p class="school-subtitle">
            Jornada Matutina · Sistema institucional
          </p>
        </div>
      </div>
    </section>

    <section class="right-panel">
      <div class="login-card">
        <div class="sgad-badge">
          SGAD
        </div>

        <h2>
          Bienvenida al sistema
        </h2>

        <p class="welcome-text">
          Ingrese con la cuenta asignada por Dirección.
        </p>

        <div class="orange-line"></div>

        <form @submit.prevent="iniciarSesion">
          <div class="form-group">
            <label for="correo">
              Correo institucional
            </label>

            <input
              id="correo"
              v-model.trim="correo"
              type="email"
              placeholder="Correo institucional"
              autocomplete="email"
              :disabled="cargando"
            />
          </div>

          <div class="form-group">
            <label for="password">
              Contraseña
            </label>

            <div class="password-row">
              <input
                id="password"
                v-model="password"
                :type="mostrarPassword ? 'text' : 'password'"
                placeholder="Contraseña"
                autocomplete="current-password"
                :disabled="cargando"
              />

              <button
                type="button"
                class="show-password-button"
                :disabled="cargando"
                @click="mostrarPassword = !mostrarPassword"
              >
                {{
                  mostrarPassword
                    ? "Ocultar"
                    : "Ver"
                }}
              </button>
            </div>
          </div>

          <p
            v-if="mensajeError"
            class="error-message"
          >
            {{ mensajeError }}
          </p>

          <button
            class="login-button"
            type="submit"
            :disabled="cargando"
          >
            {{
              cargando
                ? "Ingresando..."
                : "Ingresar al sistema"
            }}
          </button>
        </form>

        <div class="demo-section">
          <p>
            Accesos de demostración
          </p>

        </div>
      </div>
    </section>
  </main>
</template>

<script>
import {
  login
} from "../../services/authService";

export default {
  name: "LoginView",

  data() {
    return {
      correo: "",
      password: "",
      mostrarPassword: false,
      cargando: false,
      mensajeError: ""
    };
  },

  methods: {

    async iniciarSesion() {
      this.mensajeError =
        "";

      if (
        !this.correo ||
        !this.password
      ) {
        this.mensajeError =
          "Ingrese su correo institucional y contraseña.";

        return;
      }

      this.cargando =
        true;

      try {
        const data =
          await login(
            this.correo,
            this.password
          );
if (data.requires_2fa) {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("usuario");

  sessionStorage.setItem(
    "sgad_desafio_2fa",
    data.desafio
  );

  sessionStorage.setItem(
    "sgad_2fa_setup",
    String(data.requires_setup)
  );

  this.password = "";

  await this.$router.replace(
    "/verificacion-2fa"
  );

  return;
}


        localStorage.setItem(
          "access_token",
          data.access_token
        );

        localStorage.setItem(
          "refresh_token",
          data.refresh_token
        );

        localStorage.setItem(
          "usuario",
          JSON.stringify(
            data.usuario
          )
        );

        /*
         * Evitamos que un usuario nuevo
         * herede el ciclo seleccionado
         * por una sesión anterior.
         */
        localStorage.removeItem(
          "sgad_ciclo"
        );

        const rol =
          data.usuario?.rol;

        if (
          rol === "Directora"
        ) {
          await this.$router.replace(
            "/directora/dashboard"
          );

          return;
        }

        if (
          rol === "Docente"
        ) {
          await this.$router.replace(
            "/docente/dashboard"
          );

          return;
        }

        /*
         * Si apareciera un rol no soportado,
         * eliminamos la sesión creada.
         */
        localStorage.removeItem(
          "access_token"
        );

        localStorage.removeItem(
          "refresh_token"
        );

        localStorage.removeItem(
          "usuario"
        );

        this.mensajeError =
          "La cuenta no tiene un perfil habilitado en el sistema.";

      } catch (error) {
        const respuesta =
          error.response?.data;

        this.mensajeError =
          respuesta?.message ||
          respuesta?.mensaje ||
          "Correo o contraseña incorrectos.";

      } finally {
        this.cargando =
          false;
      }
    }
  }
};
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 58% 42%;
  font-family:
    Arial,
    Helvetica,
    sans-serif;
  background: #f5fbfd;
}

.left-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 50px;
  background:
    linear-gradient(
      135deg,
      #f8fcfd 0%,
      #edf8fb 55%,
      #e7f5f8 100%
    );
}

.school-info {
  width: 100%;
  max-width: 690px;
  display: flex;
  align-items: center;
  gap: 30px;
}

.logo-wrapper {
  width: 290px;
  min-width: 290px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-wrapper img {
  width: 100%;
  max-width: 290px;
  height: auto;
  object-fit: contain;
}

.school-text {
  flex: 1;
}

.school-type {
  margin: 0 0 16px;
  color: #237c98;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 1.2px;
}

.school-text h1 {
  margin: 0;
  color: #204e7e;
  font-size: 46px;
  line-height: 0.98;
  font-weight: 700;
}

.school-subtitle {
  margin: 24px 0 0;
  color: #707b83;
  font-size: 16px;
}

.right-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 55px 50px;
}

.login-card {
  width: 100%;
  max-width: 470px;
  padding: 40px;
  background: #ffffff;
  border: 1px solid #dde5e9;
  border-radius: 30px;
  box-shadow:
    0 22px 60px
    rgba(54, 85, 104, 0.08);
}

.sgad-badge {
  width: fit-content;
  padding: 11px 19px;
  margin-bottom: 27px;
  background: #225887;
  color: #ffffff;
  border-radius: 13px;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1.5px;
}

.login-card h2 {
  margin: 0;
  color: #173f67;
  font-size: 31px;
  line-height: 1.15;
}

.welcome-text {
  margin: 14px 0 18px;
  color: #7d8790;
  font-size: 16px;
}

.orange-line {
  width: 100%;
  height: 3px;
  margin-bottom: 17px;
  background: #ef843f;
}

.form-group {
  margin-bottom: 17px;
}

.form-group label {
  display: block;
  margin-bottom: 9px;
  color: #17384f;
  font-size: 14px;
  font-weight: 700;
}

.form-group input {
  width: 100%;
  height: 49px;
  padding: 0 14px;
  border: 1px solid #d5dde2;
  border-radius: 12px;
  background: #ffffff;
  color: #263947;
  font-size: 15px;
  outline: none;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.form-group input:focus {
  border-color: #4c82ad;
  box-shadow:
    0 0 0 3px
    rgba(52, 112, 159, 0.1);
}

.password-row {
  display: flex;
  gap: 10px;
}

.password-row input {
  flex: 1;
}

.show-password-button {
  width: 60px;
  border: 1px solid #d5dde2;
  border-radius: 12px;
  background: #f9fbfc;
  color: #173f67;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.show-password-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.login-button {
  width: 100%;
  height: 49px;
  margin-top: 1px;
  border: none;
  border-radius: 11px;
  background: #225887;
  color: #ffffff;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition:
    background 0.2s ease,
    transform 0.2s ease;
}

.login-button:hover:not(:disabled) {
  background: #194a75;
  transform: translateY(-1px);
}

.login-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error-message {
  margin: 0 0 15px;
  padding: 10px 12px;
  border-radius: 9px;
  background: #fff1ed;
  color: #b15037;
  font-size: 13px;
}

.demo-section {
  margin-top: 27px;
  padding-top: 22px;
  border-top: 1px solid #e1e7ea;
}

.demo-section p {
  margin: 0 0 13px;
  color: #687781;
  font-size: 14px;
}

.demo-buttons {
  display: flex;
  gap: 10px;
}

.demo-buttons button {
  flex: 1;
  min-height: 38px;
  padding: 9px 12px;
  border: 1px solid #d5dde2;
  border-radius: 9px;
  background: #f9fbfc;
  color: #456275;
  font-size: 13px;
  cursor: pointer;
}

.demo-buttons button:hover:not(:disabled) {
  background: #f0f6f9;
}

.demo-buttons button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@media (max-width: 1000px) {
  .login-page {
    grid-template-columns: 1fr;
  }

  .left-panel {
    padding: 45px 25px 25px;
  }

  .school-info {
    justify-content: center;
  }

  .right-panel {
    padding: 25px 25px 50px;
  }
}

@media (max-width: 700px) {
  .school-info {
    flex-direction: column;
    text-align: center;
  }

  .logo-wrapper {
    width: 210px;
    min-width: auto;
  }

  .school-text h1 {
    font-size: 38px;
  }

  .login-card {
    padding: 30px 24px;
  }

  .demo-buttons {
    flex-direction: column;
  }
}
</style>