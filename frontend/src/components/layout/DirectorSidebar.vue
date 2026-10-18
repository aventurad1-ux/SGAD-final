<template>
  <aside class="director-sidebar">
    <!-- Logo / identidad -->
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

    <!-- Navegación -->
    <nav class="sidebar-menu">
      <p class="menu-section">Principal</p>

      <RouterLink
        to="/directora/dashboard"
        class="menu-item"
      >
        <span class="menu-icon">▦</span>
        <span class="menu-text">Panel general</span>
      </RouterLink>

      <a class="menu-item" href="#">
        <span class="menu-icon">✓</span>
        <span class="menu-text">Bandeja de revisión</span>
        <span class="menu-count">1</span>
      </a>

      <a class="menu-item" href="#">
        <span class="menu-icon">▤</span>
        <span class="menu-text">
          Repositorio institucional
        </span>
      </a>

      <p class="menu-section">Gestión escolar</p>

      <a class="menu-item" href="#">
        <span class="menu-icon">⊙</span>
        <span class="menu-text">
          Matrículas y expedientes
        </span>
        <span class="menu-count">11</span>
      </a>

      <a class="menu-item" href="#">
        <span class="menu-icon">▱</span>
        <span class="menu-text">
          Ciclos, grados y secciones
        </span>
      </a>

      <a class="menu-item" href="#">
        <span class="menu-icon">◷</span>
        <span class="menu-text">
          Solicitudes de entrega
        </span>
        <span class="menu-count">3</span>
      </a>

      <p class="menu-section">Administración</p>

      <a class="menu-item" href="#">
        <span class="menu-icon">♟</span>
        <span class="menu-text">
          Usuarios y permisos
        </span>
      </a>

      <a class="menu-item" href="#">
        <span class="menu-icon">▥</span>
        <span class="menu-text">Reportes</span>
      </a>

      <a class="menu-item" href="#">
        <span class="menu-icon">♻</span>
        <span class="menu-text">Papelera</span>
      </a>

      <p class="menu-section">Seguridad</p>

      <a class="menu-item" href="#">
        <span class="menu-icon">▥</span>
        <span class="menu-text">
          Copias de seguridad
        </span>
      </a>

      <a class="menu-item" href="#">
        <span class="menu-icon">☷</span>
        <span class="menu-text">
          Bitácora de actividad
        </span>
      </a>
    </nav>

    <!-- Cerrar sesión -->
    <div class="sidebar-footer">
      <button
        class="logout-button"
        type="button"
        @click="cerrarSesion"
      >
        Cerrar sesión
      </button>
    </div>
  </aside>
</template>

<script>
export default {
  name: "DirectorSidebar",

  methods: {
    cerrarSesion() {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("usuario");

      this.$router.push("/");
    }
  }
};
</script>