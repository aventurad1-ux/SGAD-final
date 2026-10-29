<template>
  <header class="director-topbar">
    <div class="topbar-left">
      <strong class="topbar-sgad">
        SGAD
      </strong>

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

        <select
          v-model="cicloSeleccionado"
          @change="cambiarCiclo"
        >
          <option
            v-for="ciclo in ciclos"
            :key="ciclo.id_ciclo"
            :value="String(ciclo.id_ciclo)"
          >
            {{
              ciclo.estado === "activo"
                ? `${ciclo.anio} · Actual`
                : `${ciclo.anio} · Histórico`
            }}
          </option>
        </select>
      </div>

      <!-- ==========================================
           NOTIFICACIONES
      =========================================== -->

      <div
        ref="notificationWrap"
        class="director-notification-wrap"
      >
        <button
          class="notification-button"
          type="button"
          title="Notificaciones"
          @click.stop="alternarNotificaciones"
        >
          <span class="notification-icon">
            🔔
          </span>

          <span
            v-if="notificacionesNoLeidas > 0"
            class="notification-count"
          >
            {{ notificacionesNoLeidas }}
          </span>
        </button>

        <div
          v-if="mostrarNotificaciones"
          class="director-notification-menu"
          @click.stop
        >
          <div class="director-notification-header">
            <div>
              <strong>
                Notificaciones
              </strong>

              <span>
                {{
                  notificacionesNoLeidas === 1
                    ? "1 sin leer"
                    : `${notificacionesNoLeidas} sin leer`
                }}
              </span>
            </div>

            <button
              v-if="notificacionesNoLeidas > 0"
              type="button"
              class="director-mark-read"
              @click="marcarTodas"
            >
              Marcar todas
            </button>
          </div>

          <div
            v-if="cargandoNotificaciones"
            class="director-notification-empty"
          >
            Cargando notificaciones...
          </div>

          <div
            v-else-if="notificaciones.length === 0"
            class="director-notification-empty"
          >
            <span class="director-notification-empty-icon">
              🔔
            </span>

            <strong>
              Sin notificaciones
            </strong>

            <small>
              No hay notificaciones para este ciclo.
            </small>
          </div>

          <div
            v-else
            class="director-notification-list"
          >
            <button
              v-for="notificacion in notificaciones"
              :key="notificacion.id_notificacion"
              type="button"
              class="director-notification-item"
              :class="{
                unread: !notificacion.leida
              }"
              @click="abrirNotificacion(notificacion)"
            >
              <span
                class="director-notification-dot"
                :class="{
                  read: notificacion.leida
                }"
              ></span>

              <span class="director-notification-content">
                <strong>
                  {{ notificacion.titulo }}
                </strong>

                <small>
                  {{ notificacion.mensaje }}
                </small>

                <em
                  v-if="notificacion.fecha_creacion"
                >
                  {{
                    formatearFechaHora(
                      notificacion.fecha_creacion
                    )
                  }}
                </em>
              </span>

              <span class="director-notification-arrow">
                ›
              </span>
            </button>
          </div>
        </div>
      </div>

      <!-- ==========================================
           PERFIL
      =========================================== -->


      <button
        class="profile-summary"
        type="button"
        title="Ir a mi perfil"
        @click="$router.push('/directora/perfil')"
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
import {
  obtenerCiclos
} from "../../services/ciclosService";

import {
  obtenerNotificaciones,
  marcarNotificacionLeida,
  marcarTodasNotificacionesLeidas
} from "../../services/notificationsService";


export default {
  name: "DirectorTopbar",

  data() {
    return {
      ciclos: [],
      cicloSeleccionado: "",

      nombreUsuario: "",
      rolUsuario: "",
      iniciales: "",

      mostrarNotificaciones: false,
      cargandoNotificaciones: false,

      notificaciones: [],
      notificacionesNoLeidas: 0
    };
  },

  async mounted() {
    this.cargarUsuario();

    await this.cargarCiclos();

    await this.cargarNotificaciones();

    window.addEventListener(
      "sgad-cycle-changed",
      this.sincronizarCiclo
    );

    window.addEventListener(
      "sgad-notifications-changed",
      this.cargarNotificaciones
    );

    document.addEventListener(
      "click",
      this.cerrarNotificacionesFuera
    );
  },

  beforeUnmount() {
    window.removeEventListener(
      "sgad-cycle-changed",
      this.sincronizarCiclo
    );

    window.removeEventListener(
      "sgad-notifications-changed",
      this.cargarNotificaciones
    );

    document.removeEventListener(
      "click",
      this.cerrarNotificacionesFuera
    );
  },

  methods: {
    /* =====================================================
       USUARIO
    ===================================================== */

    cargarUsuario() {
      const usuarioGuardado =
        localStorage.getItem(
          "usuario"
        );

      if (!usuarioGuardado) {
        this.nombreUsuario =
          "Directora SGAD";

        this.rolUsuario =
          "Directora";

        this.iniciales =
          "DS";

        return;
      }

      try {
        const usuario =
          JSON.parse(
            usuarioGuardado
          );

        const nombres =
          usuario.nombres || "";

        const apellidos =
          usuario.apellidos || "";

        this.nombreUsuario =
          `${nombres} ${apellidos}`
            .trim() ||
          "Directora SGAD";

        this.rolUsuario =
          usuario.rol ||
          "Directora";

        this.iniciales =
          `${nombres.charAt(0)}${apellidos.charAt(0)}`
            .toUpperCase() ||
          "DS";

      } catch (error) {
        console.error(
          "No fue posible leer el usuario:",
          error
        );

        this.nombreUsuario =
          "Directora SGAD";

        this.rolUsuario =
          "Directora";

        this.iniciales =
          "DS";
      }
    },


    /* =====================================================
       CICLOS
    ===================================================== */

    async cargarCiclos() {
      try {
        const data =
          await obtenerCiclos();

        this.ciclos =
          data.ciclos || [];

        const cicloRuta =
          this.$route.query.id_ciclo;

        const cicloGuardado =
          localStorage.getItem(
            "sgad_ciclo"
          );

        let seleccionado =
          cicloRuta ||
          cicloGuardado ||
          "";

        const existe =
          this.ciclos.some(
            ciclo =>
              String(
                ciclo.id_ciclo
              ) ===
              String(
                seleccionado
              )
          );

        if (!existe) {
          const cicloActual =
            this.ciclos.find(
              ciclo =>
                ciclo.estado ===
                "activo"
            );

          seleccionado =
            cicloActual?.id_ciclo ||
            this.ciclos[0]?.id_ciclo ||
            "";
        }

        this.cicloSeleccionado =
          String(
            seleccionado
          );

        if (
          this.cicloSeleccionado
        ) {
          localStorage.setItem(
            "sgad_ciclo",
            this.cicloSeleccionado
          );
        }

      } catch (error) {
        console.error(
          "No fue posible cargar los ciclos:",
          error
        );
      }
    },


    async cambiarCiclo() {
      if (
        !this.cicloSeleccionado
      ) {
        return;
      }

      const idCiclo =
        Number(
          this.cicloSeleccionado
        );

      localStorage.setItem(
        "sgad_ciclo",
        String(idCiclo)
      );

      window.dispatchEvent(
        new CustomEvent(
          "sgad-cycle-changed",
          {
            detail: {
              id_ciclo:
                idCiclo
            }
          }
        )
      );

      this.mostrarNotificaciones =
        false;

      await this.cargarNotificaciones();

      if (
        this.$route.path ===
        "/directora/ciclo-escolar"
      ) {
        this.$router.replace({
          query: {
            ...this.$route.query,
            id_ciclo:
              idCiclo
          }
        });
      }
    },


    async sincronizarCiclo(event) {
      const idCiclo =
        event.detail?.id_ciclo;

      if (!idCiclo) {
        return;
      }

      this.cicloSeleccionado =
        String(idCiclo);

      localStorage.setItem(
        "sgad_ciclo",
        String(idCiclo)
      );

      this.mostrarNotificaciones =
        false;

      await this.cargarNotificaciones();
    },


    /* =====================================================
       NOTIFICACIONES
    ===================================================== */

    async cargarNotificaciones() {
      if (
        !this.cicloSeleccionado
      ) {
        this.notificaciones = [];
        this.notificacionesNoLeidas = 0;

        return;
      }

      this.cargandoNotificaciones =
        true;

      try {
        const data =
          await obtenerNotificaciones(
            Number(
              this.cicloSeleccionado
            )
          );

        this.notificaciones =
          data.notificaciones || [];

        this.notificacionesNoLeidas =
          Number(
            data.no_leidas || 0
          );

      } catch (error) {
        console.error(
          "No fue posible cargar las notificaciones:",
          error
        );

        this.notificaciones = [];

        this.notificacionesNoLeidas =
          0;

      } finally {
        this.cargandoNotificaciones =
          false;
      }
    },


    async alternarNotificaciones() {
      this.mostrarNotificaciones =
        !this.mostrarNotificaciones;

      if (
        this.mostrarNotificaciones
      ) {
        await this.cargarNotificaciones();
      }
    },


    cerrarNotificacionesFuera(event) {
      if (
        !this.mostrarNotificaciones
      ) {
        return;
      }

      const contenedor =
        this.$refs.notificationWrap;

      if (
        contenedor &&
        !contenedor.contains(
          event.target
        )
      ) {
        this.mostrarNotificaciones =
          false;
      }
    },


    async abrirNotificacion(
      notificacion
    ) {
      try {
        if (
          !notificacion.leida
        ) {
          await marcarNotificacionLeida(
            notificacion.id_notificacion
          );

          notificacion.leida =
            true;

          if (
            this.notificacionesNoLeidas > 0
          ) {
            this.notificacionesNoLeidas -= 1;
          }
        }

        this.mostrarNotificaciones =
          false;

        if (
          notificacion.ruta
        ) {
          if (
            this.$route.path ===
            notificacion.ruta
          ) {
            await this.cargarNotificaciones();

          } else {
            await this.$router.push(
              notificacion.ruta
            );
          }
        }

      } catch (error) {
        console.error(
          "No fue posible abrir la notificación:",
          error
        );
      }
    },


    async marcarTodas() {
      try {
        await marcarTodasNotificacionesLeidas(
          Number(
            this.cicloSeleccionado
          )
        );

        this.notificaciones =
          this.notificaciones.map(
            notificacion => ({
              ...notificacion,
              leida: true
            })
          );

        this.notificacionesNoLeidas =
          0;

      } catch (error) {
        console.error(
          "No fue posible marcar las notificaciones:",
          error
        );
      }
    },


    /* =====================================================
       FECHAS
    ===================================================== */

    formatearFechaHora(fecha) {
      if (!fecha) {
        return "";
      }

      const valor =
        new Date(fecha);

      if (
        Number.isNaN(
          valor.getTime()
        )
      ) {
        return "";
      }

      return valor.toLocaleString(
        "es-GT",
        {
          day: "2-digit",
          month: "short",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit"
        }
      );
    }
  }
};
</script>


<style scoped>
.director-notification-wrap {
  position: relative;
}

.director-notification-menu {
  position: absolute;

  top: calc(100% + 12px);
  right: 0;

  width: 380px;
  max-height: 470px;

  overflow: hidden;

  background: #ffffff;

  border: 1px solid #dfe5ec;
  border-radius: 14px;

  box-shadow:
    0 16px 40px
    rgba(15, 23, 42, 0.18);

  z-index: 9999;
}

.director-notification-header {
  display: flex;

  align-items: center;
  justify-content: space-between;

  gap: 16px;

  padding: 16px 18px;

  border-bottom:
    1px solid #edf0f4;
}

.director-notification-header > div {
  display: flex;

  flex-direction: column;

  gap: 3px;
}

.director-notification-header strong {
  font-size: 15px;

  color: #0c3c5d;
}

.director-notification-header span {
  font-size: 12px;

  color: #7b8494;
}

.director-mark-read {
  border: 0;

  background: transparent;

  color: #0877b9;

  font-size: 12px;
  font-weight: 700;

  cursor: pointer;
}

.director-mark-read:hover {
  text-decoration: underline;
}

.director-notification-list {
  max-height: 390px;

  overflow-y: auto;
}

.director-notification-item {
  width: 100%;

  display: flex;

  align-items: flex-start;

  gap: 11px;

  padding: 14px 16px;

  border: 0;

  border-bottom:
    1px solid #edf0f4;

  background: #ffffff;

  text-align: left;

  cursor: pointer;

  transition:
    background 0.18s ease;
}

.director-notification-item:hover {
  background: #f7f9fc;
}

.director-notification-item.unread {
  background: #eff7ff;
}

.director-notification-item.unread:hover {
  background: #e8f3ff;
}

.director-notification-dot {
  width: 9px;
  height: 9px;

  margin-top: 6px;

  flex: 0 0 9px;

  border-radius: 50%;

  background: #0877b9;
}

.director-notification-dot.read {
  background: #c5cbd3;
}

.director-notification-content {
  min-width: 0;

  flex: 1;

  display: flex;

  flex-direction: column;

  gap: 4px;
}

.director-notification-content strong {
  color: #0d4164;

  font-size: 13px;
  line-height: 1.35;
}

.director-notification-content small {
  color: #5f6875;

  font-size: 12px;
  line-height: 1.4;
}

.director-notification-content em {
  margin-top: 2px;

  color: #929aa5;

  font-size: 11px;
  font-style: normal;
}

.director-notification-arrow {
  margin-top: 6px;

  color: #9ba4af;

  font-size: 20px;
}

.director-notification-empty {
  min-height: 160px;

  padding: 24px;

  display: flex;

  flex-direction: column;

  align-items: center;
  justify-content: center;

  gap: 6px;

  text-align: center;

  color: #758091;
}

.director-notification-empty-icon {
  margin-bottom: 3px;

  font-size: 27px;
}

.director-notification-empty strong {
  color: #394356;
}

.director-notification-empty small {
  font-size: 12px;
}

@media (max-width: 720px) {
  .director-notification-menu {
    position: fixed;

    top: 72px;
    right: 12px;
    left: 12px;

    width: auto;
  }
}
</style>