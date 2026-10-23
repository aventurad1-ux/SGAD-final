<template>
  <div class="director-layout">
    <DirectorSidebar />

    <div class="director-main">
      <DirectorTopbar />

      <main class="director-content">
        <!-- ==================================================
             VISTA 1 · SECCIONES
        =================================================== -->

        <template v-if="vista === 'secciones'">
          <section class="records-page-head">
            <div>
              <p class="records-eyebrow">
                GESTIÓN ESCOLAR
              </p>

              <h1>Expedientes</h1>

              <p class="records-subtitle">
                Seleccione el grado y sección para consultar
                sus estudiantes. Ciclo {{ ciclo?.anio || "" }}.
              </p>
            </div>

            <button
              v-if="ciclo?.editable"
              type="button"
              class="records-btn records-btn-primary records-new-button"
              @click="abrirMatricula"
            >
              Nueva matrícula
            </button>
          </section>

          <div
            v-if="mensaje"
            class="records-alert records-alert-success"
          >
            {{ mensaje }}
          </div>

          <div
            v-if="error"
            class="records-alert records-alert-error"
          >
            {{ error }}
          </div>

          <div
            v-if="ciclo && !ciclo.editable"
            class="records-info"
          >
            Está consultando un ciclo histórico.
            La información está disponible únicamente
            para lectura.
          </div>

          <div
            v-if="cargando"
            class="records-empty"
          >
            Cargando expedientes...
          </div>

          <section
            v-else
            class="records-section-grid"
          >
            <article
              v-for="seccion in secciones"
              :key="seccion.id_seccion"
              class="records-section-card"
            >
              <div class="records-section-card-top">
                <div>
                  <p class="records-card-eyebrow">
                    GRADO Y SECCIÓN
                  </p>

                  <h2>
                    {{ seccion.etiqueta }}
                  </h2>
                </div>

                <span class="records-section-count">
                  {{ seccion.estudiantes }}
                </span>
              </div>

              <p class="records-section-teacher">
                Docente responsable:
                <strong>
                  {{ seccion.docente }}
                </strong>
              </p>

              <div class="records-section-foot">
                <span
                  v-if="seccion.incompletos > 0"
                  class="records-badge records-badge-warning"
                >
                  {{ seccion.incompletos }}
                  {{
                    seccion.incompletos === 1
                      ? "incompleto"
                      : "incompletos"
                  }}
                </span>

                <span
                  v-else
                  class="records-badge records-badge-success"
                >
                  Expedientes al día
                </span>

                <button
                  type="button"
                  class="records-btn records-btn-soft records-btn-sm"
                  @click="abrirSeccion(seccion)"
                >
                  Ver estudiantes
                </button>
              </div>
            </article>

            <div
              v-if="!secciones.length"
              class="records-empty"
            >
              No hay secciones registradas para este ciclo.
            </div>
          </section>
        </template>

        <!-- ==================================================
             VISTA 2 · ESTUDIANTES
        =================================================== -->

        <template v-else>
          <section class="records-students-head">
            <div>
              <p class="records-eyebrow">
                MATRÍCULAS /
                {{ seccionSeleccionada?.etiqueta?.toUpperCase() }}
              </p>

              <h1>
                Estudiantes de
                {{ seccionSeleccionada?.etiqueta }}
              </h1>

              <p class="records-subtitle">
                Ciclo escolar {{ ciclo?.anio }}
              </p>
            </div>

            <button
              type="button"
              class="records-btn records-btn-secondary records-back-button"
              @click="volverSecciones"
            >
              ← Volver a las secciones
            </button>
          </section>

          <div
            v-if="mensaje"
            class="records-alert records-alert-success"
          >
            {{ mensaje }}
          </div>

          <div
            v-if="error"
            class="records-alert records-alert-error"
          >
            {{ error }}
          </div>

          <!-- RESUMEN -->

          <section class="records-section-summary">
            <div class="records-summary-item">
              <span>GRADO Y SECCIÓN</span>

              <strong>
                {{ seccionSeleccionada?.etiqueta }}
              </strong>
            </div>

            <div class="records-summary-item">
              <span>DOCENTE RESPONSABLE</span>

              <strong>
                {{ seccionSeleccionada?.docente }}
              </strong>
            </div>

            <div class="records-summary-item">
              <span>ESTUDIANTES MATRICULADOS</span>

              <strong>
                {{ seccionSeleccionada?.estudiantes }}
              </strong>
            </div>

            <div class="records-summary-item">
              <span>CICLO ESCOLAR</span>

              <strong>
                {{ ciclo?.anio }}
              </strong>
            </div>
          </section>

          <!-- FILTROS -->

          <section class="records-students-toolbar">
            <input
              v-model="busqueda"
              type="text"
              class="records-input"
              placeholder="Buscar estudiante, CUI o código..."
            />

            <select
              v-model="filtroEstado"
              class="records-input"
            >
              <option value="">
                Todos los expedientes
              </option>

              <option value="completo">
                Completos
              </option>

              <option value="incompleto">
                Incompletos
              </option>
            </select>
          </section>

          <!-- TABLA -->

          <section class="records-table-card">
            <div class="records-table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Estudiante</th>
                    <th>Código / CUI</th>
                    <th>Expediente</th>
                    <th>Acción</th>
                  </tr>
                </thead>

                <tbody>
                  <tr
                    v-for="estudiante in estudiantesFiltrados"
                    :key="estudiante.id_estudiante"
                  >
                    <td>
                      <div class="records-cell-title">
                        {{ estudiante.nombre }}
                      </div>

                      <div class="records-cell-sub">
                        Encargado:
                        {{ estudiante.encargado }}
                      </div>
                    </td>

                    <td>
                      <div class="records-cell-title records-code">
                        {{ estudiante.codigo }}
                      </div>

                      <div class="records-cell-sub">
                        {{ estudiante.cui }}
                      </div>
                    </td>

                    <td>
                      <span
                        class="records-badge"
                        :class="
                          estudiante.expediente.completo
                            ? 'records-badge-success'
                            : 'records-badge-warning'
                        "
                      >
                        {{
                          estudiante.expediente.completo
                            ? "Completo"
                            : "Incompleto"
                        }}
                      </span>

                      <div class="records-cell-sub">
                        {{ estudiante.expediente.entregados }}
                        /
                        {{ estudiante.expediente.total }}
                        documentos
                      </div>
                    </td>

                    <td>
                      <button
                        type="button"
                        class="records-btn records-btn-soft records-btn-sm"
                        @click="abrirExpediente(estudiante)"
                      >
                        Ver expediente
                      </button>
                    </td>
                  </tr>

                  <tr
                    v-if="!estudiantesFiltrados.length"
                  >
                    <td
                      colspan="4"
                      class="records-table-empty"
                    >
                      No hay estudiantes que coincidan
                      con los filtros.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        </template>
      </main>
    </div>

    <!-- ==================================================
         MODAL · VER EXPEDIENTE
    =================================================== -->

    <div
      v-if="modalExpediente"
      class="records-overlay"
      @click.self="cerrarExpediente"
    >
      <section class="records-modal records-modal-xl">
        <header class="records-modal-head">
          <div>
            <p>EXPEDIENTE ESTUDIANTIL</p>

            <h2>
              {{ detalle?.estudiante?.nombre }}
            </h2>
          </div>

          <button
            type="button"
            class="records-close"
            @click="cerrarExpediente"
          >
            ×
          </button>
        </header>

        <div
          v-if="cargandoDetalle"
          class="records-modal-body"
        >
          <div class="records-empty">
            Cargando expediente...
          </div>
        </div>

        <div
          v-else-if="detalle"
          class="records-modal-body records-file-body"
        >
          <!-- INFORMACIÓN DEL ESTUDIANTE -->

          <section class="records-detail-grid records-expedient-detail">
            <div class="records-detail-item">
              <label>CÓDIGO PERSONAL</label>

              <strong>
                {{ detalle.estudiante.codigo }}
              </strong>
            </div>

            <div class="records-detail-item">
              <label>CUI</label>

              <strong>
                {{ detalle.estudiante.cui }}
              </strong>
            </div>

            <div class="records-detail-item">
              <label>CICLO Y SECCIÓN</label>

              <strong>
                {{ detalle.matricula.ciclo }}
                ·
                {{ detalle.matricula.seccion }}
              </strong>
            </div>

            <div class="records-detail-item">
              <label>DOCENTE RESPONSABLE</label>

              <strong>
                {{ detalle.matricula.docente }}
              </strong>
            </div>

            <div class="records-detail-item">
              <label>ENCARGADO</label>

              <strong>
                {{ detalle.estudiante.encargado }}
                ·
                {{ detalle.estudiante.parentesco }}
              </strong>
            </div>

            <div class="records-detail-item">
              <label>TELÉFONO</label>

              <strong>
                {{ detalle.estudiante.telefono }}
              </strong>
            </div>

            <div class="records-detail-item">
              <label>ESTADO DEL EXPEDIENTE</label>

              <strong>
                {{
                  detalle.estado.completo
                    ? "Completo"
                    : "Incompleto"
                }}
              </strong>
            </div>

            <div class="records-detail-item">
              <label>AVANCE</label>

              <strong>
                {{ detalle.estado.entregados }}
                de
                {{ detalle.estado.total }}
                documentos
              </strong>
            </div>
          </section>

          <h3 class="records-list-title">
            Lista de documentos
          </h3>

          <!-- DOCUMENTOS -->

          <section class="records-requirements">
            <article
              v-for="requisito in detalle.requisitos"
              :key="requisito.id_requisito"
              class="records-requirement"
            >
              <div class="records-requirement-main">
                <div
                  class="records-requirement-state"
                  :class="
                    requisito.entregado
                      ? 'ok'
                      : 'missing'
                  "
                >
                  {{ requisito.entregado ? "✓" : "!" }}
                </div>

                <div>
                  <h3>
                    {{ requisito.nombre }}
                  </h3>

                  <p v-if="requisito.entregado">
                    Entregado ·
                    v{{ requisito.version }}
                    ·
                    {{ requisito.archivo }}
                  </p>

                  <p v-else>
                    Documento pendiente
                  </p>
                </div>
              </div>

              <div class="records-requirement-actions">
                <!-- DOCUMENTO ENTREGADO -->

                <template v-if="requisito.entregado">
                  <button
                    v-if="puedePrevisualizar(requisito.tipo_mime)"
                    type="button"
                    class="records-btn records-btn-soft records-btn-sm"
                    @click="visualizarDocumento(requisito)"
                  >
                    Ver
                  </button>

                  <button
                    type="button"
                    class="records-btn records-btn-secondary records-btn-sm"
                    @click="descargar(requisito)"
                  >
                    Descargar
                  </button>

                  <button
                    v-if="detalle.matricula.editable"
                    type="button"
                    class="records-btn records-btn-secondary records-btn-sm"
                    @click="abrirCarga(requisito, 'actualizar')"
                  >
                    Actualizar
                  </button>
                </template>

                <!-- DOCUMENTO PENDIENTE -->

                <button
                  v-else-if="detalle.matricula.editable"
                  type="button"
                  class="records-btn records-btn-primary records-btn-sm"
                  @click="abrirCarga(requisito, 'subir')"
                >
                  Subir
                </button>

                <span
                  v-else
                  class="records-muted"
                >
                  Sin documento
                </span>
              </div>
            </article>
          </section>
        </div>

        <footer
          v-if="detalle"
          class="records-modal-footer records-expedient-footer"
        >
          <button
            type="button"
            class="records-btn records-btn-secondary"
            @click="cerrarExpediente"
          >
            Cerrar
          </button>

          <button
            v-if="detalle.matricula.editable"
            type="button"
            class="records-btn records-btn-primary"
            @click="abrirCargaGeneral"
          >
            Subir documento
          </button>
        </footer>
      </section>
    </div>

    <!-- ==================================================
         MODAL · AGREGAR / ACTUALIZAR DOCUMENTO
    =================================================== -->

    <div
      v-if="modalCarga"
      class="records-overlay records-overlay-front"
      @click.self="cerrarCarga"
    >
      <section class="records-modal records-upload-modal">
        <header class="records-modal-head">
          <div>
            <p>EXPEDIENTE ESTUDIANTIL</p>

            <h2>
              {{
                modoCarga === "actualizar"
                  ? "Actualizar documento"
                  : "Agregar documento"
              }}
            </h2>
          </div>

          <button
            type="button"
            class="records-close"
            @click="cerrarCarga"
          >
            ×
          </button>
        </header>

        <div class="records-modal-body">
          <div class="records-student-notice">
            <span class="records-info-icon">i</span>

            <span>
              Estudiante:
              <strong>
                {{ detalle?.estudiante?.nombre }}
              </strong>
            </span>
          </div>

          <!-- SELECTOR DE DOCUMENTO -->

          <div class="records-form-group">
            <label class="required">
              Documento
            </label>

            <select
              v-model="formDocumento.id_requisito"
              class="records-input"
              :disabled="modoCarga === 'actualizar'"
            >
              <option value="">
                Seleccione...
              </option>

              <option
                v-for="requisito in requisitosSelector"
                :key="requisito.id_requisito"
                :value="requisito.id_requisito"
              >
                {{ requisito.nombre }}
                {{
                  requisito.entregado
                    ? "· entregado"
                    : "· pendiente"
                }}
              </option>
            </select>
          </div>

          <!-- ARCHIVO -->

          <div class="records-form-group">
            <label class="required">
              Archivo
            </label>

            <input
              ref="archivoExpediente"
              type="file"
              class="records-input records-file-input"
              accept=".pdf,.docx,.xlsx,.jpg,.jpeg,.png"
              @change="seleccionarArchivo"
            />
          </div>

          <!-- OBSERVACIONES -->

          <div class="records-form-group">
            <label>
              Observaciones
            </label>

            <textarea
              v-model.trim="formDocumento.observaciones"
              class="records-input records-observations"
            ></textarea>
          </div>

          <p class="records-file-help">
            Formatos permitidos: PDF, DOCX, XLSX, JPG, JPEG y PNG.
            Tamaño máximo: 10 MB.
          </p>

          <div
            v-if="errorModal"
            class="records-alert records-alert-error"
          >
            {{ errorModal }}
          </div>
        </div>

        <footer class="records-modal-footer">
          <button
            type="button"
            class="records-btn records-btn-secondary"
            @click="cerrarCarga"
          >
            Cancelar
          </button>

          <button
            type="button"
            class="records-btn records-btn-primary"
            :disabled="procesando"
            @click="guardarDocumento"
          >
            {{
              procesando
                ? "Guardando..."
                : "Guardar"
            }}
          </button>
        </footer>
      </section>
    </div>

    <!-- ==================================================
         MODAL · MATRÍCULA
    =================================================== -->

    <div
      v-if="modalMatricula"
      class="records-overlay"
      @click.self="cerrarMatricula"
    >
      <section class="records-modal records-modal-lg">
        <header class="records-modal-head">
          <div>
            <p>GESTIÓN ESCOLAR</p>

            <h2>Nueva matrícula</h2>
          </div>

          <button
            type="button"
            class="records-close"
            @click="cerrarMatricula"
          >
            ×
          </button>
        </header>

        <div class="records-modal-body">
          <div class="records-form-group">
            <label class="required">
              Modalidad
            </label>

            <select
              v-model="matriculaForm.modo"
              class="records-input"
            >
              <option value="new">
                Registrar estudiante nuevo
              </option>

              <option value="existing">
                Reinscribir estudiante existente
              </option>
            </select>
          </div>

          <template
            v-if="matriculaForm.modo === 'new'"
          >
            <div class="records-form-two">
              <div class="records-form-group">
                <label class="required">
                  Nombres
                </label>

                <input
                  v-model.trim="matriculaForm.nombres"
                  class="records-input"
                />
              </div>

              <div class="records-form-group">
                <label class="required">
                  Apellidos
                </label>

                <input
                  v-model.trim="matriculaForm.apellidos"
                  class="records-input"
                />
              </div>
            </div>

            <div class="records-form-two">
              <div class="records-form-group">
                <label class="required">
                  CUI
                </label>

                <input
                  v-model.trim="matriculaForm.cui"
                  maxlength="13"
                  class="records-input"
                />
              </div>

              <div class="records-form-group">
                <label class="required">
                  Fecha de nacimiento
                </label>

                <input
                  v-model="matriculaForm.fecha_nacimiento"
                  type="date"
                  class="records-input"
                />
              </div>
            </div>

            <div class="records-form-two">
              <div class="records-form-group">
                <label class="required">
                  Género
                </label>

                <select
                  v-model="matriculaForm.genero"
                  class="records-input"
                >
                  <option value="">
                    Seleccione
                  </option>

                  <option value="Femenino">
                    Femenino
                  </option>

                  <option value="Masculino">
                    Masculino
                  </option>
                </select>
              </div>

              <div class="records-form-group">
                <label class="required">
                  Teléfono
                </label>

                <input
                  v-model.trim="matriculaForm.telefono"
                  maxlength="8"
                  class="records-input"
                />
              </div>
            </div>

            <div class="records-form-group">
              <label class="required">
                Dirección
              </label>

              <input
                v-model.trim="matriculaForm.direccion"
                class="records-input"
              />
            </div>

            <div class="records-form-two">
              <div class="records-form-group">
                <label class="required">
                  Encargado
                </label>

                <input
                  v-model.trim="matriculaForm.encargado"
                  class="records-input"
                />
              </div>

              <div class="records-form-group">
                <label class="required">
                  Parentesco
                </label>

                <select
                  v-model="matriculaForm.parentesco"
                  class="records-input"
                >
                  <option value="">
                    Seleccione
                  </option>

                  <option>Madre</option>
                  <option>Padre</option>
                  <option>Abuela</option>
                  <option>Abuelo</option>
                  <option>Tutor</option>
                  <option>Otro</option>
                </select>
              </div>
            </div>
          </template>

          <div
            v-else
            class="records-form-group"
          >
            <label class="required">
              Estudiante
            </label>

            <select
              v-model="matriculaForm.id_estudiante"
              class="records-input"
            >
              <option value="">
                Seleccione estudiante
              </option>

              <option
                v-for="estudiante in estudiantesDisponibles"
                :key="estudiante.id_estudiante"
                :value="estudiante.id_estudiante"
              >
                {{ estudiante.nombre }}
                ·
                {{ estudiante.codigo }}
              </option>
            </select>

            <small
              v-if="!estudiantesDisponibles.length"
              class="records-muted"
            >
              No hay estudiantes disponibles
              para reinscribir en este ciclo.
            </small>
          </div>

          <div class="records-form-group">
            <label class="required">
              Grado y sección
            </label>

            <select
              v-model="matriculaForm.id_seccion"
              class="records-input"
            >
              <option value="">
                Seleccione sección
              </option>

              <option
                v-for="seccion in seccionesCatalogo"
                :key="seccion.id_seccion"
                :value="seccion.id_seccion"
              >
                {{ seccion.etiqueta }}
                ·
                {{ seccion.docente }}
              </option>
            </select>
          </div>

          <div
            v-if="errorModal"
            class="records-alert records-alert-error"
          >
            {{ errorModal }}
          </div>
        </div>

        <footer class="records-modal-footer">
          <button
            type="button"
            class="records-btn records-btn-secondary"
            @click="cerrarMatricula"
          >
            Cancelar
          </button>

          <button
            type="button"
            class="records-btn records-btn-primary"
            :disabled="procesando"
            @click="guardarMatricula"
          >
            {{
              procesando
                ? "Guardando..."
                : "Guardar matrícula"
            }}
          </button>
        </footer>
      </section>
    </div>
  </div>
</template>

<script>
import DirectorSidebar from "../../components/layout/DirectorSidebar.vue";
import DirectorTopbar from "../../components/layout/DirectorTopbar.vue";

import {
  obtenerExpedientes,
  obtenerCatalogosExpedientes,
  crearMatricula,
  obtenerDetalleExpediente,
  subirDocumento,
  descargarDocumento,
  verDocumento
} from "../../services/expedientesService";

import "../../assets/css/expedientes.css";

export default {
  name: "ExpedientesView",

  components: {
    DirectorSidebar,
    DirectorTopbar
  },

  data() {
    return {
      ciclo: null,
      secciones: [],
      estudiantes: [],

      vista: "secciones",
      seccionSeleccionada: null,

      busqueda: "",
      filtroEstado: "",

      cargando: true,
      procesando: false,

      mensaje: "",
      error: "",
      errorModal: "",

      modalExpediente: false,
      modalCarga: false,
      modalMatricula: false,

      cargandoDetalle: false,

      detalle: null,

      modoCarga: "subir",

      formDocumento: {
        id_requisito: "",
        archivo: null,
        observaciones: ""
      },

      seccionesCatalogo: [],
      estudiantesDisponibles: [],

      matriculaForm: {
        modo: "new",
        nombres: "",
        apellidos: "",
        cui: "",
        fecha_nacimiento: "",
        genero: "",
        direccion: "",
        encargado: "",
        parentesco: "",
        telefono: "",
        id_estudiante: "",
        id_seccion: ""
      }
    };
  },

  computed: {
    estudiantesSeccion() {
      if (!this.seccionSeleccionada) {
        return [];
      }

      return this.estudiantes.filter(
        estudiante =>
          estudiante.id_seccion ===
          this.seccionSeleccionada.id_seccion
      );
    },

    estudiantesFiltrados() {
      const texto =
        this.busqueda
          .trim()
          .toLowerCase();

      return this.estudiantesSeccion.filter(
        estudiante => {
          const nombre =
            (estudiante.nombre || "")
              .toLowerCase();

          const codigo =
            (estudiante.codigo || "")
              .toLowerCase();

          const cui =
            (estudiante.cui || "")
              .toLowerCase();

          const coincideTexto =
            !texto ||
            nombre.includes(texto) ||
            codigo.includes(texto) ||
            cui.includes(texto);

          const coincideEstado =
            !this.filtroEstado ||
            (
              this.filtroEstado === "completo"
                ? estudiante.expediente.completo
                : !estudiante.expediente.completo
            );

          return (
            coincideTexto &&
            coincideEstado
          );
        }
      );
    },

    requisitosSelector() {
      if (!this.detalle) {
        return [];
      }

      if (this.modoCarga === "actualizar") {
        return this.detalle.requisitos;
      }

      return this.detalle.requisitos.filter(
        requisito =>
          !requisito.entregado
      );
    }
  },

  async mounted() {
    await this.cargarModulo();
  },

  methods: {
    async cargarModulo() {
      this.cargando = true;
      this.error = "";

      try {
        const data =
          await obtenerExpedientes();

        this.ciclo = data.ciclo;
        this.secciones = data.secciones || [];
        this.estudiantes = data.estudiantes || [];

        if (this.seccionSeleccionada) {
          const actualizada =
            this.secciones.find(
              seccion =>
                seccion.id_seccion ===
                this.seccionSeleccionada.id_seccion
            );

          if (actualizada) {
            this.seccionSeleccionada =
              actualizada;
          }
        }

      } catch (error) {
        console.error(error);

        this.error =
          error.response?.data?.mensaje ||
          "No fue posible cargar Expedientes.";

      } finally {
        this.cargando = false;
      }
    },

    abrirSeccion(seccion) {
      this.seccionSeleccionada = seccion;
      this.vista = "estudiantes";

      this.busqueda = "";
      this.filtroEstado = "";

      window.scrollTo({
        top: 0,
        behavior: "smooth"
      });
    },

    volverSecciones() {
      this.vista = "secciones";
      this.seccionSeleccionada = null;

      this.busqueda = "";
      this.filtroEstado = "";

      window.scrollTo({
        top: 0,
        behavior: "smooth"
      });
    },

    async abrirExpediente(estudiante) {
      this.modalExpediente = true;
      this.cargandoDetalle = true;
      this.detalle = null;

      try {
        this.detalle =
          await obtenerDetalleExpediente(
            estudiante.id_estudiante,
            this.ciclo.id_ciclo
          );

      } catch (error) {
        console.error(error);

        this.error =
          error.response?.data?.mensaje ||
          "No fue posible abrir el expediente.";

        this.modalExpediente = false;

      } finally {
        this.cargandoDetalle = false;
      }
    },

    cerrarExpediente() {
      if (this.modalCarga) {
        return;
      }

      this.modalExpediente = false;
      this.detalle = null;
    },

    puedePrevisualizar(tipoMime) {
      return [
        "application/pdf",
        "image/jpeg",
        "image/png"
      ].includes(tipoMime);
    },

    async visualizarDocumento(requisito) {
      try {
        await verDocumento(
          requisito.id_documento
        );

      } catch (error) {
        console.error(error);

        this.error =
          error.response?.data?.mensaje ||
          "No fue posible abrir el documento.";
      }
    },

    async descargar(requisito) {
      try {
        await descargarDocumento(
          requisito.id_documento
        );

      } catch (error) {
        console.error(error);

        this.error =
          "No fue posible descargar el documento.";
      }
    },

    abrirCarga(requisito, modo = "subir") {
      this.modoCarga = modo;

      this.formDocumento = {
        id_requisito:
          requisito?.id_requisito || "",

        archivo: null,

        observaciones: ""
      };

      this.errorModal = "";
      this.modalCarga = true;
    },

    abrirCargaGeneral() {
      const pendientes =
        this.detalle?.requisitos?.filter(
          requisito =>
            !requisito.entregado
        ) || [];

      if (!pendientes.length) {
        this.mensaje =
          "El expediente ya tiene todos los documentos requeridos.";

        return;
      }

      this.modoCarga = "subir";

      this.formDocumento = {
        id_requisito: "",
        archivo: null,
        observaciones: ""
      };

      this.errorModal = "";
      this.modalCarga = true;
    },

    cerrarCarga() {
      if (this.procesando) {
        return;
      }

      this.modalCarga = false;

      this.formDocumento = {
        id_requisito: "",
        archivo: null,
        observaciones: ""
      };

      this.errorModal = "";
      this.modoCarga = "subir";
    },

    seleccionarArchivo(event) {
      this.formDocumento.archivo =
        event.target.files?.[0] || null;
    },

    async guardarDocumento() {
      if (!this.formDocumento.id_requisito) {
        this.errorModal =
          "Seleccione el documento.";

        return;
      }

      if (!this.formDocumento.archivo) {
        this.errorModal =
          "Seleccione un archivo.";

        return;
      }

      this.procesando = true;
      this.errorModal = "";

      try {
        const respuesta =
          await subirDocumento(
            this.detalle.estudiante.id_estudiante,
            {
              id_ciclo:
                this.ciclo.id_ciclo,

              id_requisito:
                Number(
                  this.formDocumento.id_requisito
                ),

              observaciones:
                this.formDocumento.observaciones,

              archivo:
                this.formDocumento.archivo
            }
          );

        this.mensaje =
          respuesta.mensaje;

        this.modalCarga = false;

        this.formDocumento = {
          id_requisito: "",
          archivo: null,
          observaciones: ""
        };

        this.detalle =
          await obtenerDetalleExpediente(
            this.detalle.estudiante.id_estudiante,
            this.ciclo.id_ciclo
          );

        await this.cargarModulo();

      } catch (error) {
        console.error(error);

        this.errorModal =
          error.response?.data?.mensaje ||
          "No fue posible guardar el documento.";

      } finally {
        this.procesando = false;
      }
    },

    async abrirMatricula() {
      this.errorModal = "";

      try {
        const data =
          await obtenerCatalogosExpedientes(
            this.ciclo.id_ciclo
          );

        this.seccionesCatalogo =
          data.secciones || [];

        this.estudiantesDisponibles =
          data.estudiantes_disponibles || [];

        this.resetMatricula();

        this.modalMatricula = true;

      } catch (error) {
        console.error(error);

        this.error =
          "No fue posible preparar la matrícula.";
      }
    },

    resetMatricula() {
      this.matriculaForm = {
        modo: "new",
        nombres: "",
        apellidos: "",
        cui: "",
        fecha_nacimiento: "",
        genero: "",
        direccion: "",
        encargado: "",
        parentesco: "",
        telefono: "",
        id_estudiante: "",
        id_seccion: ""
      };
    },

    cerrarMatricula() {
      if (this.procesando) {
        return;
      }

      this.modalMatricula = false;
      this.errorModal = "";
    },

    async guardarMatricula() {
      this.errorModal = "";

      if (!this.matriculaForm.id_seccion) {
        this.errorModal =
          "Seleccione grado y sección.";

        return;
      }

      if (
        this.matriculaForm.modo === "existing" &&
        !this.matriculaForm.id_estudiante
      ) {
        this.errorModal =
          "Seleccione un estudiante.";

        return;
      }

      this.procesando = true;

      try {
        const payload = {
          ...this.matriculaForm,

          id_ciclo:
            this.ciclo.id_ciclo,

          id_seccion:
            Number(
              this.matriculaForm.id_seccion
            )
        };

        if (
          payload.modo === "existing"
        ) {
          payload.id_estudiante =
            Number(
              payload.id_estudiante
            );
        }

        const respuesta =
          await crearMatricula(
            payload
          );

        this.mensaje =
          respuesta.mensaje;

        this.modalMatricula = false;

        await this.cargarModulo();

      } catch (error) {
        console.error(error);

        this.errorModal =
          error.response?.data?.mensaje ||
          "No fue posible guardar la matrícula.";

      } finally {
        this.procesando = false;
      }
    }
  }
};
</script>