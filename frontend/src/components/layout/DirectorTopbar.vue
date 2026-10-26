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

      <button
        class="notification-button"
        type="button"
        title="Notificaciones"
      >
        <span class="notification-icon">
          🔔
        </span>

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
import {
  obtenerCiclos
} from "../../services/ciclosService";

export default {
  name: "DirectorTopbar",

  data() {
    return {
      ciclos: [],
      cicloSeleccionado: "",

      nombreUsuario: "",
      rolUsuario: "",
      iniciales: ""
    };
  },

  async mounted() {
    this.cargarUsuario();

    await this.cargarCiclos();

    window.addEventListener(
      "sgad-cycle-changed",
      this.sincronizarCiclo
    );
  },

  beforeUnmount() {
    window.removeEventListener(
      "sgad-cycle-changed",
      this.sincronizarCiclo
    );
  },

  methods: {
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

    cambiarCiclo() {
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

    sincronizarCiclo(event) {
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
    }
  }
};
</script>