
<template>
  <main class="pagina">
    <section class="tarjeta">
      <div class="marca">SGAD · Seguridad</div>

      <h1>Verificación de identidad</h1>

      <p class="descripcion">
        Proteja su cuenta con Google Authenticator.
      </p>

      <p v-if="error" class="error">
        {{ error }}
      </p>

      <p v-if="cargando">
        Procesando solicitud...
      </p>

      <template v-if="etapa === 'configurar'">
        <h2>Configurar Google Authenticator</h2>

        <p>
          Abra Google Authenticator en su teléfono,
          seleccione agregar cuenta y escanee
          este código QR.
        </p>

        <img
          v-if="imagenQR"
          :src="imagenQR"
          class="qr"
          alt="QR para configurar Google Authenticator"
        />

        <p class="ayuda">
          Después de escanearlo, escriba el código
          de seis dígitos que aparece en su teléfono.
        </p>

        <form @submit.prevent="confirmarActivacion">
          <input
            v-model="codigo"
            placeholder="000000"
            maxlength="6"
            inputmode="numeric"
            autocomplete="one-time-code"
            required
          />

          <button :disabled="cargando">
            Activar protección
          </button>
        </form>
      </template>

      <template v-else-if="etapa === 'recuperacion'">
        <h2>Guarde sus códigos de recuperación</h2>

        <p>
          Estos códigos permiten recuperar el
          acceso si pierde su teléfono.
          Cada uno puede utilizarse una sola vez.
        </p>

        <div class="codigos">
          <code
            v-for="item in codigosRecuperacion"
            :key="item"
          >
            {{ item }}
          </code>
        </div>

        <button @click="copiarCodigos">
          Copiar códigos
        </button>

        <p class="ayuda">
          Guárdelos en un lugar privado.
          No los comparta ni los deje en una
          computadora pública.
        </p>

        <button @click="continuarVerificacion">
          Ya guardé mis códigos
        </button>
      </template>

      <template v-else-if="etapa === 'verificar'">
        <h2>
  {{
    modoRecuperacion
      ? "Ingrese su código de recuperación"
      : "Ingrese su código de seguridad"
  }}
</h2>
        <p>
          Abra Google Authenticator e ingrese
          el código actual de seis dígitos.
        </p>

        <form @submit.prevent="confirmarIngreso">

<input
  v-model.trim="codigo"
  :placeholder="modoRecuperacion ? 'Código de recuperación' : '000000'"
  :maxlength="modoRecuperacion ? 16 : 6"
  :inputmode="modoRecuperacion ? 'text' : 'numeric'"
  :autocomplete="modoRecuperacion ? 'off' : 'one-time-code'"
  required
/>


          <button :disabled="cargando">
            Verificar e ingresar
          </button>
        </form>


<button
  type="button"
  class="volver"
  :disabled="cargando"
  @click="cambiarModoRecuperacion"
>
  {{
    modoRecuperacion
      ? "Usar Google Authenticator"
      : "¿Perdió su teléfono? Usar código de recuperación"
  }}
</button>


        <p class="ayuda">
          Si acaba de activar Google Authenticator,
          espere a que aparezca un código nuevo.
        </p>
      </template>

      <button class="volver" @click="volverLogin">
        Volver al inicio de sesión
      </button>
    </section>
  </main>
</template>

<script>
import QRCode from "qrcode";

import {
  preparar2FA,
  activar2FA,
  verificar2FA,
  recuperarAcceso2FA
} from "../../services/authService";

export default {
  name: "SegundoFactorView",

  data() {
    return {
      desafio: "",
      etapa: "verificar",
      codigo: "",
      modoRecuperacion: false,
      imagenQR: "",
      codigosRecuperacion: [],
      cargando: false,
      error: ""
    };
  },

  async mounted() {
    this.desafio =
      sessionStorage.getItem("sgad_desafio_2fa") || "";

    if (!this.desafio) {
      this.$router.replace("/");
      return;
    }

    const requiereConfiguracion =
      sessionStorage.getItem("sgad_2fa_setup") === "true";

    if (requiereConfiguracion) {
      this.etapa = "configurar";
      await this.cargarQR();
    }
  },

  methods: {
    async cargarQR() {
      this.cargando = true;
      this.error = "";

      try {
        const respuesta = await preparar2FA(
          this.desafio
        );

        this.imagenQR = await QRCode.toDataURL(
          respuesta.provisioning_uri,
          {
            width: 240,
            margin: 2
          }
        );
      } catch (error) {
        this.error =
          error.response?.data?.message ||
          "No se pudo preparar Google Authenticator.";
      } finally {
        this.cargando = false;
      }
    },

    async confirmarActivacion() {
      this.error = "";
      this.cargando = true;

      try {
        const respuesta = await activar2FA(
          this.desafio,
          this.codigo.trim()
        );

        this.codigosRecuperacion =
          respuesta.codigos_recuperacion || [];

        this.codigo = "";
        this.imagenQR = "";
        this.etapa = "recuperacion";

        sessionStorage.setItem(
          "sgad_2fa_setup", "false"
        );
      } catch (error) {
        this.error =
          error.response?.data?.message ||
          "No se pudo activar el segundo factor.";
      } finally {
        this.cargando = false;
      }
    },

    async copiarCodigos() {
      try {
        await navigator.clipboard.writeText(
          this.codigosRecuperacion.join("\n")
        );
      } catch {
        this.error =
          "No se pudieron copiar los códigos.";
      }
    },

    continuarVerificacion() {
      this.codigosRecuperacion = [];
      this.codigo = "";
      this.etapa = "verificar";
    },

    async confirmarIngreso() {
      this.error = "";
      this.cargando = true;

      try {
        const data = this.modoRecuperacion
  ? await recuperarAcceso2FA(
      this.desafio,
      this.codigo.trim()
    )
  : await verificar2FA(
      this.desafio,
      this.codigo.trim()
    );
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
          JSON.stringify(data.usuario)
        );

        localStorage.removeItem("sgad_ciclo");

        sessionStorage.removeItem(
          "sgad_desafio_2fa"
        );
        sessionStorage.removeItem(
          "sgad_2fa_setup"
        );

        if (data.usuario?.rol === "Directora") {
          await this.$router.replace(
            "/directora/dashboard"
          );
        } else if (data.usuario?.rol === "Docente") {
          await this.$router.replace(
            "/docente/dashboard"
          );
        } else {
          this.volverLogin();
        }
      } catch (error) {
        this.error =
          error.response?.data?.message ||
          "Código incorrecto o vencido.";
      } finally {
        this.cargando = false;
      }
    },

    cambiarModoRecuperacion() {
  this.modoRecuperacion = !this.modoRecuperacion;
  this.codigo = "";
  this.error = "";
},

    volverLogin() {
      sessionStorage.removeItem(
        "sgad_desafio_2fa"
      );
      sessionStorage.removeItem(
        "sgad_2fa_setup"
      );
      this.$router.replace("/");
    }
  }
};
</script>

<style scoped>
.pagina {
  min-height: 100vh;
  background: #edf7fa;
  display: grid;
  place-items: center;
  padding: 24px;
  font-family: Arial, sans-serif;
}

.tarjeta {
  background: white;
  padding: 36px;
  width: 100%;
  max-width: 460px;
  border-radius: 22px;
  box-shadow: 0 12px 40px #143b5b18;
  text-align: center;
}

.marca {
  display: inline-block;
  padding: 10px 17px;
  border-radius: 9px;
  background: #225887;
  color: white;
  font-weight: bold;
}

h1 {
  font-size: 26px;
  color: #173f67;
}

h2 {
  font-size: 19px;
  color: #173f67;
}

.descripcion,
.ayuda,
p {
  color: #667988;
  line-height: 1.6;
}

.ayuda {
  font-size: 13px;
}

.qr {
  width: 240px;
  max-width: 100%;
  margin: 12px auto;
}

input {
  display: block;
  width: 100%;
  padding: 14px;
  margin: 16px 0;
  border: 1px solid #cbdce7;
  border-radius: 10px;
  text-align: center;
  font-size: 23px;
  letter-spacing: 5px;
}

button {
  background: #225887;
  color: white;
  border: none;
  border-radius: 10px;
  padding: 13px;
  cursor: pointer;
  width: 100%;
  margin-top: 10px;
  font-weight: bold;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.volver {
  background: #eef3f7;
  color: #225887;
  margin-top: 20px;
}

.error {
  color: #a92929;
  background: #fff0f0;
  border-radius: 8px;
  padding: 10px;
}

.codigos {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 9px;
  margin: 20px 0;
}

.codigos code {
  padding: 10px 4px;
  background: #edf3f8;
  border-radius: 6px;
  font-size: 12px;
}
</style>
