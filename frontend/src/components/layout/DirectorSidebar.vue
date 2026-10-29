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

      <!-- ===============================================
           BANDEJA DE REVISIÓN
      ================================================ -->

      <RouterLink
        to="/directora/revision"
        class="menu-item"
      >
        <span class="menu-icon">✓</span>

        <span class="menu-text">
          Bandeja de revisión
        </span>

        <span
          v-if="contadorRevision > 0"
          class="menu-count"
        >
          {{ contadorRevision }}
        </span>
      </RouterLink>

      <RouterLink
        to="/directora/repositorio"
        class="menu-item"
      >
        <span class="menu-icon">▤</span>

        <span class="menu-text">
          Repositorio institucional
        </span>
      </RouterLink>

      <p class="menu-section">
        Gestión escolar
      </p>

      <!-- ===============================================
           EXPEDIENTES
      ================================================ -->

      <RouterLink
        to="/directora/expedientes"
        class="menu-item"
      >
        <span class="menu-icon">⊙</span>

        <span class="menu-text">
          Expedientes
        </span>

        <span
          v-if="contadorExpedientes > 0"
          class="menu-count"
        >
          {{ contadorExpedientes }}
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

      <!-- ===============================================
           SOLICITUDES
      ================================================ -->

      <RouterLink
        to="/directora/solicitudes"
        class="menu-item"
      >
        <span class="menu-icon">◷</span>

        <span class="menu-text">
          Solicitudes de entrega
        </span>

        <span
          v-if="contadorSolicitudes > 0"
          class="menu-count"
        >
          {{ contadorSolicitudes }}
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

<RouterLink
  to="/directora/reportes"
  class="menu-item"
>
  <span class="menu-icon">▥</span>

  <span class="menu-text">
    Reportes
  </span>
</RouterLink>

      <!-- ===============================================
           PAPELERA
      ================================================ -->

      <RouterLink
        to="/directora/papelera"
        class="menu-item"
      >
        <span class="menu-icon">♻</span>

        <span class="menu-text">
          Papelera
        </span>

        <span
          v-if="contadorPapelera > 0"
          class="menu-count"
        >
          {{ contadorPapelera }}
        </span>
      </RouterLink>

      <p class="menu-section">
        Seguridad
      </p>

      <a
        href="#"
        class="menu-item"
        @click.prevent
      >
        <span class="menu-icon">▥</span>

        <span class="menu-text">
          Copias de seguridad
        </span>
      </a>

      <a
        href="#"
        class="menu-item"
        @click.prevent
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
import {
  RouterLink
} from "vue-router";

import {
  obtenerCiclos
} from "../../services/ciclosService";

import {
  obtenerSolicitudes
} from "../../services/requestsService";

import {
  obtenerBandejaRevision
} from "../../services/reviewService";

import {
  obtenerPapelera
} from "../../services/papeleraService";


export default {
  name: "DirectorSidebar",

  components: {
    RouterLink
  },


  data() {
    return {
      contadorRevision: 0,
      contadorExpedientes: 0,
      contadorSolicitudes: 0,
      contadorPapelera: 0
    };
  },


  async mounted() {
    window.addEventListener(
      "sgad-cycle-changed",
      this.manejarCambioCiclo
    );

    await this.cargarContadores();
  },


  beforeUnmount() {
    window.removeEventListener(
      "sgad-cycle-changed",
      this.manejarCambioCiclo
    );
  },


  methods: {
    /* =====================================================
       CICLO SELECCIONADO
    ===================================================== */

    obtenerIdCicloSeleccionado() {
      const valor =
        localStorage.getItem(
          "sgad_ciclo"
        );

      if (!valor) {
        return null;
      }

      try {
        const parsed =
          JSON.parse(valor);

        if (
          typeof parsed === "number"
        ) {
          return parsed;
        }

        if (
          parsed &&
          typeof parsed === "object"
        ) {
          return Number(
            parsed.id_ciclo ||
            parsed.id ||
            0
          ) || null;
        }

      } catch {
        const numero =
          Number(valor);

        return numero || null;
      }

      return null;
    },


    /* =====================================================
       EXTRAER LISTA
    ===================================================== */

    extraerLista(
      data,
      posiblesClaves = []
    ) {
      if (
        Array.isArray(data)
      ) {
        return data;
      }

      for (
        const clave
        of posiblesClaves
      ) {
        if (
          Array.isArray(
            data?.[clave]
          )
        ) {
          return data[clave];
        }
      }

      return [];
    },


    /* =====================================================
       SOLICITUD ABIERTA
    ===================================================== */

    solicitudEstaAbierta(
      solicitud
    ) {
      const estado =
        String(
          solicitud?.estado ||
          ""
        )
          .trim()
          .toLowerCase();

      const estadosCerrados = [
        "cerrada",
        "cerrado",
        "finalizada",
        "finalizado"
      ];

      return !estadosCerrados.includes(
        estado
      );
    },


    /* =====================================================
       CARGAR CONTADORES
    ===================================================== */

    async cargarContadores() {
      const idCiclo =
        this.obtenerIdCicloSeleccionado();

      try {
        const [
          dataCiclos,
          dataSolicitudes,
          dataRevision,
          dataPapelera
        ] = await Promise.all([
          obtenerCiclos(
            idCiclo
          ),

          obtenerSolicitudes(
            idCiclo
          ),

          obtenerBandejaRevision(),

          obtenerPapelera(
            idCiclo
          )
        ]);


        /* ===============================================
           EXPEDIENTES / ESTUDIANTES
        ================================================ */

        const secciones =
          Array.isArray(
            dataCiclos?.secciones
          )
            ? dataCiclos.secciones
            : [];


        const seccionesActivas =
          secciones.filter(
            (seccion) =>
              seccion.activo !== false
          );


        this.contadorExpedientes =
          seccionesActivas.reduce(
            (
              total,
              seccion
            ) => {
              return (
                total +
                Number(
                  seccion.estudiantes ||
                  0
                )
              );
            },
            0
          );


        /* ===============================================
           SOLICITUDES ABIERTAS
        ================================================ */

        const solicitudes =
          this.extraerLista(
            dataSolicitudes,
            [
              "solicitudes",
              "items",
              "data"
            ]
          );


        this.contadorSolicitudes =
          solicitudes.filter(
            this.solicitudEstaAbierta
          ).length;


        /* ===============================================
           BANDEJA DE REVISIÓN
        ================================================ */

        const revisiones =
          this.extraerLista(
            dataRevision,
            [
              "entregas",
              "revision",
              "documentos",
              "pendientes",
              "items"
            ]
          );


        if (idCiclo) {
          const revisionesDelCiclo =
            revisiones.filter(
              (item) => {
                const itemCiclo =
                  Number(
                    item.id_ciclo ||
                    item.ciclo?.id_ciclo ||
                    item.solicitud?.id_ciclo ||
                    0
                  );

                if (!itemCiclo) {
                  return true;
                }

                return (
                  itemCiclo ===
                  Number(idCiclo)
                );
              }
            );

          this.contadorRevision =
            revisionesDelCiclo.length;

        } else {
          this.contadorRevision =
            revisiones.length;
        }


        /* ===============================================
           PAPELERA
        ================================================ */

        const documentosPapelera =
          this.extraerLista(
            dataPapelera,
            [
              "documentos",
              "items",
              "data"
            ]
          );


        this.contadorPapelera =
          documentosPapelera.length;

      } catch (error) {
        console.error(
          "ERROR CONTADORES SIDEBAR:",
          error
        );
      }
    },


    /* =====================================================
       CAMBIO DE CICLO
    ===================================================== */

    async manejarCambioCiclo() {
      await this.cargarContadores();
    },


    /* =====================================================
       CERRAR SESIÓN
    ===================================================== */

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

