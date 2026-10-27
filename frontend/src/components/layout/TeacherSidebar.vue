<template>
  <aside class="teacher-sidebar">
    <div class="teacher-sidebar-brand">
      <img
        src="../../assets/images/logo.jpeg"
        alt="Logo de la escuela"
        class="teacher-sidebar-logo"
      />

      <div>
        <strong>SGAD</strong>
        <span>EORM Orfelinda Osorio</span>
      </div>
    </div>

    <div class="teacher-badge">
      <span class="teacher-status-dot"></span>
      DOCENTE
    </div>

    <nav class="teacher-menu">
      <p class="teacher-menu-section">
        Mi espacio
      </p>

      <RouterLink
        to="/docente/dashboard"
        class="teacher-menu-item"
      >
        <span class="teacher-menu-icon">
          ▦
        </span>

        <span>
          Mi panel
        </span>
      </RouterLink>

      <RouterLink
        to="/docente/estudiantes"
        class="teacher-menu-item"
      >
        <span class="teacher-menu-icon">
          ⊙
        </span>

        <span>
          Mis estudiantes
        </span>
      </RouterLink>

      <RouterLink
        to="/docente/solicitudes"
        class="teacher-menu-item"
      >
        <span class="teacher-menu-icon">
          ◷
        </span>

        <span>
          Entregas solicitadas
        </span>

        <span
          v-if="solicitudesPendientes > 0"
          class="teacher-menu-count"
        >
          {{ solicitudesPendientes }}
        </span>
      </RouterLink>

      <RouterLink
        to="/docente/documentos"
        class="teacher-menu-item"
      >
        <span class="teacher-menu-icon">
          ▤
        </span>

        <span>
          Mis documentos
        </span>
      </RouterLink>

      <p class="teacher-menu-section">
        Seguimiento
      </p>

      <RouterLink
        to="/docente/correcciones"
        class="teacher-menu-item"
      >
        <span class="teacher-menu-icon">
          ↻
        </span>

        <span>
          Correcciones
        </span>

        <span
          v-if="correccionesPendientes > 0"
          class="teacher-menu-count"
        >
          {{ correccionesPendientes }}
        </span>
      </RouterLink>

      <RouterLink
        to="/docente/comprobantes"
        class="teacher-menu-item"
      >
        <span class="teacher-menu-icon">
          ▧
        </span>

        <span>
          Mis comprobantes
        </span>
      </RouterLink>
    </nav>

    <div class="teacher-sidebar-footer">
      <button
        type="button"
        class="teacher-logout-button"
        @click="cerrarSesion"
      >
        Cerrar sesión
      </button>
    </div>
  </aside>
</template>

<script>
import {
  RouterLink
} from "vue-router";

import {
  obtenerSolicitudesDocente
} from "../../services/docenteSolicitudesService";


export default {
  name: "TeacherSidebar",

  components: {
    RouterLink
  },

  data() {
    return {
      solicitudesPendientes: 0,
      correccionesPendientes: 0
    };
  },

  mounted() {
    this.cargarContadores();

    window.addEventListener(
      "sgad-actualizar-contadores-docente",
      this.cargarContadores
    );
  },

  beforeUnmount() {
    window.removeEventListener(
      "sgad-actualizar-contadores-docente",
      this.cargarContadores
    );
  },

  methods: {
    obtenerIdCiclo() {
      const valor =
        localStorage.getItem(
          "sgad_ciclo"
        );

      if (!valor) {
        return null;
      }

      const numero =
        Number(valor);

      return Number.isNaN(numero)
        ? null
        : numero;
    },


    async cargarContadores() {
      try {
        const data =
          await obtenerSolicitudesDocente(
            this.obtenerIdCiclo()
          );

        const solicitudes =
          data.solicitudes || [];


        /*
         * ENTREGAS SOLICITADAS
         *
         * Cuenta solicitudes que todavía
         * necesitan que el docente entregue
         * un archivo.
         */
        this.solicitudesPendientes =
          solicitudes.filter(
            (solicitud) =>
              solicitud.estado === "pendiente"
              || solicitud.estado === "vencido"
          ).length;


        /*
         * CORRECCIONES
         *
         * Cuenta solamente solicitudes que
         * Dirección devolvió para corrección.
         */
        this.correccionesPendientes =
          solicitudes.filter(
            (solicitud) =>
              solicitud.estado
              === "correccion_solicitada"
          ).length;

      } catch (error) {
        console.error(
          "Error al cargar contadores del docente:",
          error
        );

        this.solicitudesPendientes = 0;
        this.correccionesPendientes = 0;
      }
    },


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

      this.$router.replace("/");
    }
  }
};
</script>