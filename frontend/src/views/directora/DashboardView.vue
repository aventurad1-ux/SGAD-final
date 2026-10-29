<template>
  <div class="director-layout">
    <DirectorSidebar />

    <div class="director-main">
      <DirectorTopbar />

      <main class="director-content">
        <!-- ==================================================
             HERO
        =================================================== -->

        <section class="dashboard-hero">
          <div class="hero-text">
            <p class="hero-eyebrow">
              PANEL DIRECTIVO · CICLO 2026
            </p>

            <h1>
              Bienvenida, Prof. María Eugenia
            </h1>

            <p>
              Revise matrículas, expedientes, documentos y entregas
              del ciclo seleccionado.
            </p>
          </div>

          <button
            class="upload-document-button"
            type="button"
            @click="irRepositorio"
          >
            Subir documento
          </button>
        </section>

        <!-- ==================================================
             ERROR
        =================================================== -->

        <div
          v-if="error"
          class="records-alert records-alert-error"
          style="margin-bottom: 18px;"
        >
          {{ error }}
        </div>

        <!-- ==================================================
             MÉTRICAS
        =================================================== -->

        <section class="dashboard-metrics">
          <!-- ESTUDIANTES -->

          <article class="metric-card">
            <div class="metric-top">
              <div>
                <span class="metric-label">
                  ESTUDIANTES<br />
                  MATRICULADOS
                </span>

                <strong class="metric-number">
                  {{ cargando ? "..." : estudiantesMatriculados }}
                </strong>
              </div>

              <div class="metric-icon">
                ◎
              </div>
            </div>

            <p class="metric-description">
              Estudiantes activos en este ciclo
            </p>

            <div class="metric-footer">
              <span>
                {{ expedientesIncompletos }}
                expediente{{ expedientesIncompletos === 1 ? "" : "s" }}<br />
                incompleto{{ expedientesIncompletos === 1 ? "" : "s" }}
              </span>

              <button
                type="button"
                @click="irExpedientes"
              >
                Ver detalles →
              </button>
            </div>
          </article>

          <!-- DOCENTES -->

          <article class="metric-card">
            <div class="metric-top">
              <div>
                <span class="metric-label">
                  DOCENTES<br />
                  ASIGNADOS
                </span>

                <strong class="metric-number">
                  {{ cargando ? "..." : docentesAsignados }}
                </strong>
              </div>

              <div class="metric-icon">
                ♟
              </div>
            </div>

            <p class="metric-description">
              Responsables únicos con sección
            </p>

            <div class="metric-footer">
              <span>
                {{ seccionesActivas }}
                sección{{ seccionesActivas === 1 ? "" : "es" }}<br />
                activa{{ seccionesActivas === 1 ? "" : "s" }}
              </span>

              <button
                type="button"
                @click="irCicloEscolar"
              >
                Ver detalles →
              </button>
            </div>
          </article>

          <!-- PENDIENTES -->

          <article class="metric-card">
            <div class="metric-top">
              <div>
                <span class="metric-label">
                  PENDIENTES DE<br />
                  REVISIÓN
                </span>

                <strong class="metric-number">
                  {{ cargando ? "..." : pendientesRevision }}
                </strong>
              </div>

              <div class="metric-icon">
                ✓
              </div>
            </div>

            <p class="metric-description">
              Documentos enviados por docentes
            </p>

            <div class="metric-footer">
              <span>
                Requieren<br />
                atención
              </span>

              <button
                type="button"
                @click="irRevision"
              >
                Ver detalles →
              </button>
            </div>
          </article>

          <!-- SOLICITUDES -->

          <article class="metric-card">
            <div class="metric-top">
              <div>
                <span class="metric-label">
                  SOLICITUDES<br />
                  ABIERTAS
                </span>

                <strong class="metric-number">
                  {{ cargando ? "..." : solicitudesAbiertas }}
                </strong>
              </div>

              <div class="metric-icon">
                ◷
              </div>
            </div>

            <p class="metric-description">
              Entregas programadas
            </p>

            <div class="metric-footer">
              <span>
                {{ solicitudesAbiertas }}
                vigente{{ solicitudesAbiertas === 1 ? "" : "s" }}
              </span>

              <button
                type="button"
                @click="irSolicitudes"
              >
                Ver detalles →
              </button>
            </div>
          </article>
        </section>

        <!-- ==================================================
             PARTE INFERIOR
        =================================================== -->

        <section class="dashboard-lower-grid">
          <article class="dashboard-card requests-card">
            <div class="dashboard-card-header">
              <div>
                <h2>
                  Solicitudes de entrega
                </h2>

                <p>
                  Cumplimiento docente calculado en tiempo real
                </p>
              </div>

              <button
                type="button"
                class="create-request-button"
                @click="irSolicitudes"
              >
                Crear<br />
                solicitud
              </button>
            </div>

            <div class="request-row">
              <div class="request-status-icon">
                ◷
              </div>

              <div class="request-info">
                <strong>
                  Planificación de Unidad IV
                </strong>

                <span>
                  Vence: 20 oct 2026 · 1/4 entregaron
                </span>

                <div class="request-progress">
                  <div
                    class="request-progress-fill"
                    style="width: 25%"
                  ></div>
                </div>
              </div>

              <button
                type="button"
                class="request-view-button"
                @click="irSolicitudes"
              >
                Ver
              </button>
            </div>

            <div class="request-row">
              <div class="request-status-icon">
                ◷
              </div>

              <div class="request-info">
                <strong>
                  Cuadros de calificaciones · IV Bimestre
                </strong>

                <span>
                  Vence: 25 oct 2026 · 0/4 entregaron
                </span>

                <div class="request-progress">
                  <div
                    class="request-progress-fill"
                    style="width: 0%"
                  ></div>
                </div>
              </div>

              <button
                type="button"
                class="request-view-button"
                @click="irSolicitudes"
              >
                Ver
              </button>
            </div>

            <div class="request-row">
              <div class="request-status-icon">
                ◷
              </div>

              <div class="request-info">
                <strong>
                  Reporte mensual de asistencia
                </strong>

                <span>
                  Vence: 31 oct 2026 · 0/4 entregaron
                </span>

                <div class="request-progress">
                  <div
                    class="request-progress-fill"
                    style="width: 0%"
                  ></div>
                </div>
              </div>

              <button
                type="button"
                class="request-view-button"
                @click="irSolicitudes"
              >
                Ver
              </button>
            </div>
          </article>

          <!-- ==================================================
               ACTIVIDAD
          =================================================== -->

          <article class="dashboard-card activity-card">
            <div class="dashboard-card-header">
              <div>
                <h2>
                  Actividad reciente
                </h2>

                <p>
                  Movimientos registrados en el sistema
                </p>
              </div>

              <button
                type="button"
                class="activity-log-button"
              >
                Ver bitácora
              </button>
            </div>

            <div class="activity-row">
              <div class="activity-icon">
                ✓
              </div>

              <div>
                <strong>
                  Inició sesión
                </strong>

                <span>
                  Acceso correcto al sistema · 15/10/2026,
                  09:28 p. m.
                </span>
              </div>
            </div>

            <div class="activity-row">
              <div class="activity-icon">
                ✓
              </div>

              <div>
                <strong>
                  Inició sesión
                </strong>

                <span>
                  Acceso correcto al sistema · 15/10/2026,
                  09:24 p. m.
                </span>
              </div>
            </div>

            <div class="activity-row">
              <div class="activity-icon">
                ✓
              </div>

              <div>
                <strong>
                  Cerró sesión
                </strong>

                <span>
                  Cierre correcto · 11/10/2026,
                  08:47 a. m.
                </span>
              </div>
            </div>

            <div class="activity-row">
              <div class="activity-icon">
                ✓
              </div>

              <div>
                <strong>
                  Inició sesión
                </strong>

                <span>
                  Acceso correcto al sistema · 11/10/2026,
                  08:46 a. m.
                </span>
              </div>
            </div>

            <div class="activity-row">
              <div class="activity-icon">
                ✓
              </div>

              <div>
                <strong>
                  Cerró sesión
                </strong>

                <span>
                  Cierre correcto · 11/10/2026,
                  08:46 a. m.
                </span>
              </div>
            </div>
          </article>
        </section>
      </main>
    </div>
  </div>
</template>


<script setup>
import {
  ref,
  onMounted,
  onBeforeUnmount
} from "vue";

import {
  useRouter
} from "vue-router";

import DirectorSidebar from "../../components/layout/DirectorSidebar.vue";
import DirectorTopbar from "../../components/layout/DirectorTopbar.vue";

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
  obtenerExpedientes
} from "../../services/expedientesService";

import "../../assets/css/director.css";


const router = useRouter();


const cargando =
  ref(true);

const error =
  ref("");


const estudiantesMatriculados =
  ref(0);

const docentesAsignados =
  ref(0);

const pendientesRevision =
  ref(0);

const solicitudesAbiertas =
  ref(0);

const expedientesIncompletos =
  ref(0);

const seccionesActivas =
  ref(0);


/* =========================================================
   CICLO SELECCIONADO
========================================================= */

function obtenerIdCicloSeleccionado() {
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
}


/* =========================================================
   UTILIDAD PARA OBTENER LISTAS
========================================================= */

function extraerLista(
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
}


/* =========================================================
   ESTADO DE SOLICITUD
========================================================= */

function solicitudEstaAbierta(
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
}


/* =========================================================
   CARGAR DASHBOARD
========================================================= */

async function cargarDashboard() {
  cargando.value = true;
  error.value = "";

  try {
    const idCiclo =
      obtenerIdCicloSeleccionado();

    const [
      dataCiclos,
      dataSolicitudes,
      dataRevision,
      dataExpedientes
    ] = await Promise.all([
      obtenerCiclos(
        idCiclo
      ),

      obtenerSolicitudes(
        idCiclo
      ),

      obtenerBandejaRevision(),

      obtenerExpedientes(
        idCiclo
      )
    ]);


    /* =====================================================
       CICLO / SECCIONES
    ===================================================== */

    const secciones =
      Array.isArray(
        dataCiclos?.secciones
      )
        ? dataCiclos.secciones
        : [];


    const seccionesActivasLista =
      secciones.filter(
        (seccion) =>
          seccion.activo !== false
      );


    seccionesActivas.value =
      seccionesActivasLista.length;


    estudiantesMatriculados.value =
      seccionesActivasLista.reduce(
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


    const docentesUnicos =
      new Set(
        seccionesActivasLista
          .map(
            (seccion) =>
              seccion.id_docente
          )
          .filter(
            Boolean
          )
      );


    docentesAsignados.value =
      docentesUnicos.size;


    /* =====================================================
       SOLICITUDES
    ===================================================== */

    const solicitudes =
      extraerLista(
        dataSolicitudes,
        [
          "solicitudes",
          "items",
          "data"
        ]
      );


    solicitudesAbiertas.value =
      solicitudes.filter(
        solicitudEstaAbierta
      ).length;


    /* =====================================================
       BANDEJA DE REVISIÓN
    ===================================================== */

    const revisiones =
      extraerLista(
        dataRevision,
        [
          "entregas",
          "revision",
          "documentos",
          "pendientes",
          "items"
        ]
      );


    pendientesRevision.value =
      revisiones.length;


    /* =====================================================
       EXPEDIENTES INCOMPLETOS
    ===================================================== */

    const expedientes =
      extraerLista(
        dataExpedientes,
        [
          "expedientes",
          "estudiantes",
          "items"
        ]
      );


    expedientesIncompletos.value =
      expedientes.filter(
        (item) => {
          const estado =
            String(
              item.estado_expediente ||
              item.estado ||
              ""
            )
              .trim()
              .toLowerCase();

          if (
            estado === "incompleto"
          ) {
            return true;
          }

          if (
            item.completo === false
          ) {
            return true;
          }

          return false;
        }
      ).length;

  } catch (err) {
    console.error(
      "ERROR DASHBOARD:",
      err
    );

    error.value =
      err.response?.data?.mensaje ||
      "No fue posible cargar los indicadores del panel.";

  } finally {
    cargando.value = false;
  }
}


/* =========================================================
   CAMBIO DE CICLO
========================================================= */

async function manejarCambioCiclo() {
  await cargarDashboard();
}


/* =========================================================
   NAVEGACIÓN
========================================================= */

function irExpedientes() {
  router.push(
    "/directora/expedientes"
  );
}


function irCicloEscolar() {
  router.push(
    "/directora/ciclo-escolar"
  );
}


function irRevision() {
  router.push(
    "/directora/revision"
  );
}


function irSolicitudes() {
  router.push(
    "/directora/solicitudes"
  );
}


function irRepositorio() {
  router.push(
    "/directora/repositorio"
  );
}


/* =========================================================
   CICLO DE VIDA
========================================================= */

onMounted(
  async () => {
    window.addEventListener(
      "sgad-cycle-changed",
      manejarCambioCiclo
    );

    await cargarDashboard();
  }
);


onBeforeUnmount(
  () => {
    window.removeEventListener(
      "sgad-cycle-changed",
      manejarCambioCiclo
    );
  }
);
</script>