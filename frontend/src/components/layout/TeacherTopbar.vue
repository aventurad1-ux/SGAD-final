<template>
  <header class="teacher-topbar">
    <div class="teacher-topbar-left">
      <strong class="teacher-topbar-sgad">
        SGAD
      </strong>

      <span class="teacher-topbar-line"></span>

      <span class="teacher-topbar-school">
        EORM Orfelinda Osorio Lemus
      </span>
    </div>

    <div class="teacher-topbar-right">

      <!-- ==========================================
           SELECTOR DE CICLO
      =========================================== -->

      <div
        ref="cycleWrapper"
        class="teacher-cycle-wrapper"
      >
        <button
          type="button"
          class="teacher-cycle-selector"
          @click="toggleCiclos"
        >
          <span>
            Ciclo escolar
          </span>

          <strong>
            {{
              cicloVisible
                ? `${cicloVisible.anio} · ${textoEstadoCiclo(cicloVisible)}`
                : "—"
            }}
          </strong>

          <span class="teacher-cycle-arrow">
            ⌄
          </span>
        </button>

        <div
          v-if="mostrarCiclos"
          class="teacher-cycle-menu"
        >
          <button
            v-for="item in ciclosDisponibles"
            :key="item.id_ciclo"
            type="button"
            class="teacher-cycle-option"
            :class="{
              active:
                Number(item.id_ciclo)
                === Number(cicloVisible?.id_ciclo)
            }"
            @click="seleccionarCiclo(item)"
          >
            <span>
              {{ item.anio }}
            </span>

            <small>
              {{
                item.estado === "activo"
                  ? "Actual"
                  : "Histórico"
              }}
            </small>
          </button>
        </div>
      </div>

      <!-- ==========================================
           NOTIFICACIONES
      =========================================== -->

      <div
        ref="notificationWrapper"
        class="teacher-notification-wrapper"
      >
        <button
          type="button"
          class="teacher-notification-button"
          title="Notificaciones"
          @click="toggleNotificaciones"
        >
          <span class="teacher-bell">
            🔔
          </span>

          <span
            v-if="notificaciones > 0"
            class="teacher-notification-count"
          >
            {{ notificaciones }}
          </span>
        </button>

        <div
          v-if="mostrarNotificaciones"
          class="teacher-notification-menu"
        >
          <div class="teacher-notification-header">
            <strong>
              Notificaciones
            </strong>

            <span>
              {{ notificaciones }}
            </span>
          </div>

          <div
            v-if="!itemsNotificaciones.length"
            class="teacher-notification-empty"
          >
            No hay notificaciones pendientes.
          </div>

          <button
            v-for="item in itemsNotificaciones"
            :key="`${item.tipo}-${item.id}`"
            type="button"
            class="teacher-notification-item"
            @click="abrirNotificacion(item)"
          >
            <span
              class="teacher-notification-item-icon"
              :class="{
                correction:
                  item.tipo === 'correccion'
              }"
            >
              {{
                item.tipo === "correccion"
                  ? "↻"
                  : "◷"
              }}
            </span>

            <span class="teacher-notification-item-content">
              <strong>
                {{ item.titulo }}
              </strong>

              <small>
                {{ item.mensaje }}
              </small>

              <em
                v-if="item.fecha_limite"
              >
                Vence
                {{ formatearFecha(item.fecha_limite) }}
              </em>
            </span>
          </button>
        </div>
      </div>

      <!-- ==========================================
           PERFIL DOCENTE
      =========================================== -->

      <button
        type="button"
        class="teacher-profile teacher-profile-button"
        title="Mi perfil"
        @click="irPerfil"
      >
        <div class="teacher-avatar">

          <img
            v-if="fotoUrl"
            :src="fotoUrl"
            alt="Foto de perfil"
            class="teacher-avatar-image"
          />

          <span v-else>
            {{ iniciales }}
          </span>

        </div>

        <div class="teacher-profile-text">
          <strong>
            {{ nombreUsuario }}
          </strong>

          <span>
            Docente
          </span>
        </div>
      </button>

    </div>
  </header>
</template>


<script>
import {
  obtenerCiclos
} from "../../services/ciclosService";

import {
  obtenerFotoPerfilDocente
} from "../../services/docentePerfilService";


export default {
  name: "TeacherTopbar",


  props: {
    notificaciones: {
      type: Number,
      default: 0
    },

    itemsNotificaciones: {
      type: Array,
      default: () => []
    },

    ciclos: {
      type: Array,
      default: () => []
    },

    cicloSeleccionado: {
      type: Object,
      default: null
    }
  },


  emits: [
    "cambiar-ciclo",
    "abrir-notificacion"
  ],


  data() {
    return {
      cicloInterno: null,
      ciclosInternos: [],

      nombreUsuario: "Docente",
      iniciales: "D",

      fotoUrl: null,

      mostrarCiclos: false,
      mostrarNotificaciones: false
    };
  },


  computed: {
    cicloVisible() {
      return (
        this.cicloSeleccionado
        || this.cicloInterno
        || null
      );
    },


    ciclosDisponibles() {
      if (
        this.ciclos
        && this.ciclos.length
      ) {
        return this.ciclos;
      }

      return this.ciclosInternos;
    }
  },


  async mounted() {
    this.cargarUsuario();

    await this.cargarFotoPerfil();

    /*
     * Si el Dashboard no envía ciclos,
     * el Topbar puede cargarlos solo.
     */
    if (
      !this.ciclos
      || !this.ciclos.length
    ) {
      await this.cargarCiclos();
    }

    document.addEventListener(
      "click",
      this.cerrarMenusDesdeFuera
    );

    /*
     * Cuando el docente modifica su perfil
     * o cambia su fotografía, actualizamos
     * inmediatamente el Topbar.
     */
    window.addEventListener(
      "sgad-perfil-actualizado",
      this.actualizarPerfilTopbar
    );
  },


  beforeUnmount() {
    document.removeEventListener(
      "click",
      this.cerrarMenusDesdeFuera
    );

    window.removeEventListener(
      "sgad-perfil-actualizado",
      this.actualizarPerfilTopbar
    );

    this.liberarFoto();
  },


  methods: {

    // =====================================================
    // USUARIO
    // =====================================================

    cargarUsuario() {
      try {
        const usuario =
          JSON.parse(
            localStorage.getItem(
              "usuario"
            ) || "{}"
          );

        const nombres =
          usuario.nombres || "";

        const apellidos =
          usuario.apellidos || "";

        this.nombreUsuario =
          `${nombres} ${apellidos}`.trim()
          || "Docente";

        this.iniciales =
          `${nombres.charAt(0)}${apellidos.charAt(0)}`
            .toUpperCase()
          || "D";

      } catch {
        this.nombreUsuario =
          "Docente";

        this.iniciales =
          "D";
      }
    },


    // =====================================================
    // FOTO DE PERFIL
    // =====================================================

    async cargarFotoPerfil() {
      this.liberarFoto();

      try {
        const response =
          await obtenerFotoPerfilDocente();

        if (
          response
          && response.data
        ) {
          this.fotoUrl =
            URL.createObjectURL(
              response.data
            );
        }

      } catch {
        /*
         * Si todavía no existe foto,
         * simplemente mostramos las iniciales.
         */
        this.fotoUrl = null;
      }
    },


    liberarFoto() {
      if (this.fotoUrl) {
        URL.revokeObjectURL(
          this.fotoUrl
        );

        this.fotoUrl = null;
      }
    },


    async actualizarPerfilTopbar() {
      this.cargarUsuario();

      await this.cargarFotoPerfil();
    },


    // =====================================================
    // IR A MI PERFIL
    // =====================================================

    irPerfil() {
      this.mostrarCiclos = false;
      this.mostrarNotificaciones = false;

      this.$router.push(
        "/docente/perfil"
      );
    },


    // =====================================================
    // CICLOS
    // =====================================================

    async cargarCiclos() {
      try {
        const data =
          await obtenerCiclos();

        this.ciclosInternos =
          data.ciclos || [];

        const cicloGuardado =
          Number(
            localStorage.getItem(
              "sgad_ciclo"
            )
          );

        let seleccionado =
          null;

        if (
          cicloGuardado
          && !Number.isNaN(
            cicloGuardado
          )
        ) {
          seleccionado =
            this.ciclosInternos.find(
              item =>
                Number(
                  item.id_ciclo
                ) === cicloGuardado
            );
        }

        this.cicloInterno =
          seleccionado
          || this.ciclosInternos.find(
            item =>
              item.estado === "activo"
          )
          || data.ciclo
          || null;

        if (this.cicloInterno) {
          localStorage.setItem(
            "sgad_ciclo",
            String(
              this.cicloInterno.id_ciclo
            )
          );

          /*
           * Guardamos también el año para
           * poder mostrarlo en otras vistas.
           */
          localStorage.setItem(
            "sgad_ciclo_anio",
            String(
              this.cicloInterno.anio
            )
          );
        }

      } catch (error) {
        console.error(
          "No fue posible cargar los ciclos:",
          error
        );
      }
    },


    toggleCiclos(event) {
      event.stopPropagation();

      this.mostrarCiclos =
        !this.mostrarCiclos;

      this.mostrarNotificaciones =
        false;
    },


    seleccionarCiclo(
      ciclo
    ) {
      if (!ciclo) {
        return;
      }

      this.cicloInterno =
        ciclo;

      localStorage.setItem(
        "sgad_ciclo",
        String(
          ciclo.id_ciclo
        )
      );

      localStorage.setItem(
        "sgad_ciclo_anio",
        String(
          ciclo.anio
        )
      );

      this.mostrarCiclos =
        false;

      this.$emit(
        "cambiar-ciclo",
        ciclo
      );

      window.dispatchEvent(
        new Event(
          "sgad-actualizar-contadores-docente"
        )
      );
    },


    // =====================================================
    // NOTIFICACIONES
    // =====================================================

    toggleNotificaciones(event) {
      event.stopPropagation();

      this.mostrarNotificaciones =
        !this.mostrarNotificaciones;

      this.mostrarCiclos =
        false;
    },


    abrirNotificacion(
      item
    ) {
      this.mostrarNotificaciones =
        false;

      this.$emit(
        "abrir-notificacion",
        item
      );
    },


    // =====================================================
    // CERRAR MENÚS
    // =====================================================

    cerrarMenusDesdeFuera(event) {
      const cicloDentro =
        this.$refs.cycleWrapper
        && this.$refs.cycleWrapper.contains(
          event.target
        );

      const notificacionDentro =
        this.$refs.notificationWrapper
        && this.$refs.notificationWrapper.contains(
          event.target
        );

      if (!cicloDentro) {
        this.mostrarCiclos =
          false;
      }

      if (!notificacionDentro) {
        this.mostrarNotificaciones =
          false;
      }
    },


    // =====================================================
    // TEXTOS
    // =====================================================

    textoEstadoCiclo(
      ciclo
    ) {
      if (!ciclo) {
        return "";
      }

      return ciclo.estado === "activo"
        ? "Actual"
        : "Histórico";
    },


    formatearFecha(
      valor
    ) {
      if (!valor) {
        return "";
      }

      const fecha =
        new Date(
          `${valor}T00:00:00`
        );

      return fecha.toLocaleDateString(
        "es-GT",
        {
          day: "2-digit",
          month: "short",
          year: "numeric"
        }
      );
    }
  }
};
</script>