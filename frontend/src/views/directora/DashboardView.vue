<template>
  <div class="director-layout">
    <DirectorSidebar />

    <div class="director-main">
      <DirectorTopbar />

      <main class="director-content">
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
          >
            Subir documento
          </button>
        </section>

        <section class="dashboard-metrics">
          <article class="metric-card">
            <div class="metric-top">
              <div>
                <span class="metric-label">
                  ESTUDIANTES<br />
                  MATRICULADOS
                </span>

                <strong class="metric-number">
                  11
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
                4 expedientes<br />
                incompletos
              </span>

              <button type="button">
                Ver detalles →
              </button>
            </div>
          </article>

          <article class="metric-card">
            <div class="metric-top">
              <div>
                <span class="metric-label">
                  DOCENTES<br />
                  ASIGNADOS
                </span>

                <strong class="metric-number">
                  4
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
                6 secciones<br />
                activas
              </span>

              <button type="button">
                Ver detalles →
              </button>
            </div>
          </article>

          <article class="metric-card">
            <div class="metric-top">
              <div>
                <span class="metric-label">
                  PENDIENTES DE<br />
                  REVISIÓN
                </span>

                <strong class="metric-number">
                  1
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

              <button type="button">
                Ver detalles →
              </button>
            </div>
          </article>

          <article class="metric-card">
            <div class="metric-top">
              <div>
                <span class="metric-label">
                  SOLICITUDES<br />
                  ABIERTAS
                </span>

                <strong class="metric-number">
                  3
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
                3 vigentes
              </span>

              <button type="button">
                Ver detalles →
              </button>
            </div>
          </article>
        </section>

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

              <button type="button" class="request-view-button">
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

              <button type="button" class="request-view-button">
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

              <button type="button" class="request-view-button">
                Ver
              </button>
            </div>
          </article>

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
import DirectorSidebar from "../../components/layout/DirectorSidebar.vue";
import DirectorTopbar from "../../components/layout/DirectorTopbar.vue";
import "../../assets/css/director.css";
</script>