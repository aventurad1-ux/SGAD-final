<template>
  <aside class="director-sidebar">
    <div class="sidebar-brand">
      <img
        src="../../assets/images/logo.jpeg"
        alt="Logo de la escuela"
        class="sidebar-logo"
      />

      <div class="brand-text">
        <strong>SGAD</strong>
        <span>EORM Orfelinda Osorio</span>
      </div>
    </div>

    <div class="director-badge">
      <span class="status-dot"></span>
      DIRECCIÓN GENERAL
    </div>

    <nav class="sidebar-menu">
      <p class="menu-section">
        Principal
      </p>

      <RouterLink
        to="/directora/dashboard"
        class="menu-item"
      >
        <span class="menu-icon">▦</span>

        <span class="menu-text">
          Panel general
        </span>
      </RouterLink>

      <RouterLink
        to="/directora/revision"
        class="menu-item"
      >
        <span class="menu-icon">✓</span>

        <span class="menu-text">
          Bandeja de revisión
        </span>

        <span class="menu-count">
          1
        </span>
      </RouterLink>

      <a
        href="#"
        class="menu-item"
      >
        <span class="menu-icon">▤</span>

        <span class="menu-text">
          Repositorio institucional
        </span>
      </a>

      <p class="menu-section">
        Gestión escolar
      </p>

      <RouterLink
        to="/directora/expedientes"
        class="menu-item"
      >
        <span class="menu-icon">⊙</span>

        <span class="menu-text">
          Expedientes
        </span>
      </RouterLink>

      <RouterLink
        to="/directora/ciclo-escolar"
        class="menu-item"
      >
        <span class="menu-icon">▱</span>

        <span class="menu-text">
          Ciclo escolar
        </span>
      </RouterLink>

      <RouterLink
        to="/directora/solicitudes"
        class="menu-item"
      >
        <span class="menu-icon">◷</span>

        <span class="menu-text">
          Solicitudes de entrega
        </span>

        <span class="menu-count">
          3
        </span>
      </RouterLink>

      <p class="menu-section">
        Administración
      </p>

      <RouterLink
        to="/directora/usuarios"
        class="menu-item"
      >
        <span class="menu-icon">♟</span>

        <span class="menu-text">
          Usuarios y permisos
        </span>
      </RouterLink>

      <a
        href="#"
        class="menu-item"
      >
        <span class="menu-icon">▥</span>

        <span class="menu-text">
          Reportes
        </span>
      </a>

      <a
        href="#"
        class="menu-item"
      >
        <span class="menu-icon">♻</span>

        <span class="menu-text">
          Papelera
        </span>
      </a>

      <p class="menu-section">
        Seguridad
      </p>

      <a
        href="#"
        class="menu-item"
      >
        <span class="menu-icon">▥</span>

        <span class="menu-text">
          Copias de seguridad
        </span>
      </a>

      <a
        href="#"
        class="menu-item"
      >
        <span class="menu-icon">☷</span>

        <span class="menu-text">
          Bitácora de actividad
        </span>
      </a>
    </nav>

    <div class="sidebar-footer">
      <button
        type="button"
        class="logout-button"
        @click="cerrarSesion"
      >
        Cerrar sesión
      </button>
    </div>
  </aside>
</template>

<script>
import { RouterLink } from "vue-router";

export default {
  name: "DirectorSidebar",

  components: {
    RouterLink
  },

  methods: {
    cerrarSesion() {
      localStorage.removeItem(
        "access_token"
      );

      localStorage.removeItem(
        "refresh_token"
      );

      localStorage.removeItem(
        "usuario"
      );

      localStorage.removeItem(
        "sgad_ciclo"
      );

      this.$router.push("/");
    }
  }
};
</script>
