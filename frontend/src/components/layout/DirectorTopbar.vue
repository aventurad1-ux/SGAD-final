<template>
  <header class="director-topbar">
    <div class="topbar-left">
      <strong class="topbar-sgad">SGAD</strong>

      <span class="topbar-separator"></span>

      <span class="topbar-school">
        EORM Orfelinda Osorio Lemus
      </span>
    </div>

    <div class="topbar-right">
      <div class="cycle-box">
        <span class="cycle-label">
          Ciclo escolar
        </span>

        <select v-model="cicloSeleccionado">
          <option value="2026">
            2026 · Actual
          </option>

          <option value="2025">
            2025
          </option>

          <option value="2024">
            2024
          </option>
        </select>
      </div>

      <button
        class="notification-button"
        type="button"
        title="Notificaciones"
      >
        <span class="notification-icon">🔔</span>

        <span class="notification-count">
          2
        </span>
      </button>

      <button
        class="profile-summary"
        type="button"
      >
        <div class="profile-avatar">
           {{ iniciales }}
        </div>

        <div class="profile-text">
          <strong>
             {{ nombreUsuario }}
          </strong>

          <span>
             {{ rolUsuario }}
          </span>
        </div>
      </button>
    </div>
  </header>
</template>

<script>
export default {
  name: "DirectorTopbar",

  data() {
    return {
      cicloSeleccionado: "2026",
      nombreUsuario: "",
      rolUsuario: "",
      iniciales: ""
    };
  },

  mounted() {
    const usuarioGuardado =
      localStorage.getItem("usuario");

    if (usuarioGuardado) {
      try {
        const usuario =
          JSON.parse(usuarioGuardado);

        const nombres =
          usuario.nombres || "";

        const apellidos =
          usuario.apellidos || "";

        this.nombreUsuario =
          `${nombres} ${apellidos}`.trim();

        this.rolUsuario =
          usuario.rol || "";
        
        this.iniciales =
          `${nombres.charAt(0)}${apellidos.charAt(0)}`
            .toUpperCase();

      } catch {
        this.nombreUsuario =
          "Usuario";
        this.rolUsuario =
          "";
        this.iniciales =
          "U";
      }
    }
  }
};
</script>