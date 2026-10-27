<template>
  <div class="teacher-layout">
    <TeacherSidebar />

    <div class="teacher-main">
      <TeacherTopbar />

      <main class="teacher-content">
        <section class="students-page-head">
          <p>
            ESPACIO DOCENTE
          </p>

          <h1>
            Mis estudiantes
          </h1>

          <span>
            Información de las secciones que tiene asignadas.
          </span>
        </section>

        <div
          v-if="error"
          class="teacher-alert-error"
        >
          {{ error }}
        </div>

        <!-- FILTROS -->

        <section class="students-filters">
          <div class="students-search">
            <input
              v-model.trim="busqueda"
              type="text"
              placeholder="Buscar por nombre o código..."
            />
          </div>

          <select
            v-model="seccionSeleccionada"
          >
            <option value="">
              Todas mis secciones
            </option>

            <option
              v-for="seccion in secciones"
              :key="seccion.id_seccion"
              :value="String(seccion.id_seccion)"
            >
              {{ seccion.etiqueta }}
            </option>
          </select>

          <select
            v-model="estadoExpediente"
          >
            <option value="">
              Todos los expedientes
            </option>

            <option value="completo">
              Completos
            </option>

            <option value="pendiente">
              Pendientes
            </option>
          </select>
        </section>

        <!-- TABLA -->

        <section class="students-table-card">
          <div
            v-if="cargando"
            class="students-empty"
          >
            Cargando estudiantes...
          </div>

          <div
            v-else-if="!estudiantesFiltrados.length"
            class="students-empty"
          >
            No se encontraron estudiantes.
          </div>

          <div
            v-else
            class="students-table-wrap"
          >
            <table class="students-table">
              <thead>
                <tr>
                  <th>
                    ESTUDIANTE
                  </th>

                  <th>
                    SECCIÓN
                  </th>

                  <th>
                    EXPEDIENTE
                  </th>

                  <th>
                    ACCIÓN
                  </th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="estudiante in estudiantesFiltrados"
                  :key="estudiante.id_estudiante"
                >
                  <td>
                    <div class="student-main-info">
                      <strong>
                        {{ estudiante.nombre }}
                      </strong>

                      <span>
                        {{ estudiante.codigo }}
                      </span>
                    </div>
                  </td>

                  <td>
                    {{ estudiante.seccion }}
                  </td>

                  <td>
                    <span
                      :class="[
                        'student-expediente-badge',
                        estudiante.expediente?.completo
                          ? 'complete'
                          : 'pending'
                      ]"
                    >
                      {{
                        estudiante.expediente?.completo
                          ? "Completo"
                          : "Pendiente"
                      }}
                    </span>
                  </td>

                  <td>
                    <button
                      type="button"
                      class="student-consult-btn"
                      @click="abrirExpediente(estudiante)"
                    >
                      Consultar
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- MODAL CONSULTA DE EXPEDIENTE -->

        <div
          v-if="mostrarExpediente"
          class="student-consult-overlay"
          @click.self="cerrarExpediente"
        >
          <section class="student-consult-modal">

            <!-- ENCABEZADO -->

            <header class="student-consult-header">
              <div>
                <p>
                  CONSULTA DE EXPEDIENTE
                </p>

                <h2>
                  {{ detalle?.estudiante?.nombre }}
                </h2>
              </div>

              <button
                type="button"
                class="student-consult-close-x"
                @click="cerrarExpediente"
              >
                ×
              </button>
            </header>

            <!-- CARGANDO -->

            <div
              v-if="cargandoDetalle"
              class="student-consult-loading"
            >
              Cargando expediente...
            </div>

            <!-- CUERPO -->

            <div
              v-else-if="detalle"
              class="student-consult-body"
            >
              <div class="student-consult-info">
                <span class="student-consult-info-icon">
                  i
                </span>

                <span>
                  Vista docente de solo consulta.
                  Estado:

                  <strong>
                    {{
                      detalle.estado.completo
                        ? "Completo"
                        : "Pendiente"
                    }}.
                  </strong>
                </span>
              </div>

              <!-- DOCUMENTOS -->

              <div class="student-consult-documents">
                <article
                  v-for="requisito in detalle.requisitos"
                  :key="requisito.id_requisito"
                  class="student-consult-document"
                >
                  <div class="student-consult-document-left">
                    <div
                      :class="[
                        'student-consult-document-status',
                        requisito.entregado
                          ? 'delivered'
                          : 'pending'
                      ]"
                    >
                      {{
                        requisito.entregado
                          ? "✓"
                          : "!"
                      }}
                    </div>

                    <div class="student-consult-document-text">
                      <strong>
                        {{ requisito.nombre }}
                      </strong>

                      <span>
                        {{
                          requisito.entregado
                            ? "Documento entregado"
                            : "Documento pendiente"
                        }}
                      </span>
                    </div>
                  </div>

                  <button
                    v-if="requisito.entregado"
                    type="button"
                    class="student-consult-download"
                    @click="descargarDocumento(requisito)"
                  >
                    Descargar
                  </button>

                  <span
                    v-else
                    class="student-consult-pending-text"
                  >
                    Pendiente
                  </span>
                </article>
              </div>
            </div>

            <!-- PIE -->

            <footer class="student-consult-footer">
              <button
                type="button"
                @click="cerrarExpediente"
              >
                Cerrar
              </button>
            </footer>
          </section>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import TeacherSidebar
  from "../../components/layout/TeacherSidebar.vue";

import TeacherTopbar
  from "../../components/layout/TeacherTopbar.vue";

import {
  obtenerMisEstudiantes,
  obtenerMiEstudiante,
  descargarDocumentoDocente
} from "../../services/docenteEstudiantesService";

import "../../assets/css/teacher-students.css";


export default {
  name: "TeacherStudentsView",

  components: {
    TeacherSidebar,
    TeacherTopbar
  },

  data() {
    return {
      secciones: [],
      estudiantes: [],

      busqueda: "",
      seccionSeleccionada: "",
      estadoExpediente: "",

      cargando: true,
      error: "",

      mostrarExpediente: false,
      cargandoDetalle: false,
      detalle: null,

      ciclo: null
    };
  },

  computed: {
    estudiantesFiltrados() {
      let resultado = [
        ...this.estudiantes
      ];

      if (
        this.seccionSeleccionada
      ) {
        resultado =
          resultado.filter(
            estudiante =>
              String(
                estudiante.id_seccion
              ) ===
              String(
                this.seccionSeleccionada
              )
          );
      }

      if (
        this.estadoExpediente === "completo"
      ) {
        resultado =
          resultado.filter(
            estudiante =>
              estudiante.expediente?.completo
          );
      }

      if (
        this.estadoExpediente === "pendiente"
      ) {
        resultado =
          resultado.filter(
            estudiante =>
              !estudiante.expediente?.completo
          );
      }

      const termino =
        this.busqueda
          .toLowerCase()
          .trim();

      if (termino) {
        resultado =
          resultado.filter(
            estudiante =>
              estudiante.nombre
                ?.toLowerCase()
                .includes(termino)
              ||
              estudiante.codigo
                ?.toLowerCase()
                .includes(termino)
          );
      }

      return resultado;
    }
  },

  async mounted() {
    await this.cargarDatos();
  },

  methods: {
    async cargarDatos() {
      this.cargando = true;
      this.error = "";

      try {
        const idCiclo =
          Number(
            localStorage.getItem(
              "sgad_ciclo"
            )
          ) || null;

        const data =
          await obtenerMisEstudiantes(
            idCiclo
          );

        this.ciclo =
          data.ciclo;

        this.secciones =
          data.secciones || [];

        this.estudiantes =
          data.estudiantes || [];

      } catch (error) {
        console.error(error);

        this.error =
          error.response?.data?.mensaje ||
          error.response?.data?.message ||
          "No fue posible cargar sus estudiantes.";

      } finally {
        this.cargando =
          false;
      }
    },

    async abrirExpediente(
      estudiante
    ) {
      this.mostrarExpediente =
        true;

      this.cargandoDetalle =
        true;

      this.detalle =
        null;

      try {
        this.detalle =
          await obtenerMiEstudiante(
            estudiante.id_estudiante,
            this.ciclo.id_ciclo
          );

      } catch (error) {
        console.error(error);

        this.error =
          error.response?.data?.mensaje ||
          "No fue posible abrir el expediente.";

        this.mostrarExpediente =
          false;

      } finally {
        this.cargandoDetalle =
          false;
      }
    },

    cerrarExpediente() {
      this.mostrarExpediente =
        false;

      this.detalle =
        null;
    },

    async descargarDocumento(
      requisito
    ) {
      try {
        const response =
          await descargarDocumentoDocente(
            requisito.id_documento
          );

        const blob =
          new Blob(
            [response.data],
            {
              type:
                response.headers[
                  "content-type"
                ]
            }
          );

        const url =
          URL.createObjectURL(
            blob
          );

        const enlace =
          document.createElement(
            "a"
          );

        enlace.href =
          url;

        enlace.download =
          requisito.archivo ||
          "documento";

        document.body.appendChild(
          enlace
        );

        enlace.click();

        enlace.remove();

        URL.revokeObjectURL(
          url
        );

      } catch (error) {
        console.error(error);

        alert(
          "No fue posible descargar el documento."
        );
      }
    }
  }
};
</script>