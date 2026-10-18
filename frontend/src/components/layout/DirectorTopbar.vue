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
          ME
        </div>

        <div class="profile-text">
          <strong>
            María Eugenia Morales Soto
          </strong>

          <span>
            Directora
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
      cicloSeleccionado: "2026"
    };
  }
};
</script>