<template>
  <div class="director-layout">
    <DirectorSidebar />

    <div class="director-main">
      <DirectorTopbar />

      <main class="director-content">
        <section class="requests-page-head">
          <div>
            <p class="requests-eyebrow">
              GESTIÓN DOCUMENTAL
            </p>

            <h1>Solicitudes de entrega</h1>

            <p class="requests-subtitle">
              Solicite documentos y supervise el
              cumplimiento de cada docente.
            </p>
          </div>

          <button
            v-if="cicloActivo"
            class="requests-btn requests-btn-primary"
            type="button"
            @click="abrirCrear"
          >
            Crear solicitud
          </button>
        </section>

        <div
          v-if="mensaje"
          class="requests-alert requests-alert-success"
        >
          {{ mensaje }}
        </div>

        <div
          v-if="error"
          class="requests-alert requests-alert-error"
        >
          {{ error }}
        </div>

        <div
          v-if="cargando"
          class="requests-empty"
        >
          Cargando solicitudes...
        </div>

        <section
          v-else-if="solicitudes.length"
          class="requests-grid"
        >
          <article
            v-for="solicitud in solicitudes"
            :key="solicitud.id_solicitud"
            class="requests-card"
          >
            <div class="requests-card-head">
              <div>
                <h2>
                  {{ solicitud.titulo }}
                </h2>

                <p>
                  Vence
                  {{ formatearFecha(solicitud.fecha_limite) }}
                  ·
                  {{
                    solicitud.formatos_permitidos.join(", ")
                  }}
                </p>
              </div>

              <span
                class="requests-status"
                :class="estadoClase(solicitud.estado)"
              >
                {{ estadoTexto(solicitud.estado) }}
              </span>
            </div>

            <p class="requests-description">
              {{ solicitud.descripcion }}
            </p>

            <div class="requests-progress">
              <span
                :style="{
                  width:
                    solicitud.porcentaje_cumplimiento + '%'
                }"
              ></span>
            </div>

            <div class="requests-section-foot">
              <span>
                <strong>
                  {{ solicitud.total_entregados }}
                  /
                  {{ solicitud.total_destinatarios }}
                </strong>
                docentes entregaron
              </span>

              <div class="requests-table-actions">
                <button
                  class="requests-btn requests-btn-soft requests-btn-sm"
                  type="button"
                  @click="abrirCumplimiento(solicitud)"
                >
                  Ver cumplimiento
                </button>

                <button
                  v-if="
                    solicitud.estado === 'publicada' &&
                    cicloActivo
                  "
                  class="requests-btn requests-btn-secondary requests-btn-sm"
                  type="button"
                  @click="pedirCerrar(solicitud)"
                >
                  Cerrar
                </button>

                <button
                  v-if="
                    solicitud.estado === 'cerrada' &&
                    cicloActivo
                  "
                  class="requests-btn requests-btn-primary requests-btn-sm"
                  type="button"
                  @click="abrirReabrir(solicitud)"
                >
                  Reabrir
                </button>
              </div>
            </div>
          </article>
        </section>

        <div
          v-else
          class="requests-empty"
        >
          <h3>Sin solicitudes</h3>

          <p>
            Todavía no se han creado solicitudes
            para este ciclo.
          </p>
        </div>
      </main>
    </div>

    <!-- ================================================= -->
    <!-- CREAR SOLICITUD                                   -->
    <!-- ================================================= -->

    <div
      v-if="modalCrear"
      class="requests-overlay"
      @click.self="cerrarModales"
    >
      <section class="requests-modal requests-modal-lg">
        <header class="requests-modal-head">
          <div>
            <p>NUEVA CONVOCATORIA</p>
            <h2>Crear solicitud de entrega</h2>
          </div>

          <button
            type="button"
            class="requests-close"
            @click="cerrarModales"
          >
            ×
          </button>
        </header>

        <div class="requests-modal-body">
          <form
            id="crear-solicitud-form"
            @submit.prevent="guardarNuevaSolicitud"
          >
            <div class="requests-form-group">
              <label class="required">
                Título
              </label>

              <input
                v-model.trim="form.titulo"
                class="requests-input"
                maxlength="120"
                required
              />
            </div>

            <div class="requests-form-group">
              <label class="required">
                Descripción e instrucciones
              </label>

              <textarea
                v-model.trim="form.descripcion"
                class="requests-input"
                required
              ></textarea>
            </div>

            <div class="requests-field-row-three">
              <div class="requests-form-group">
                <label>Categoría</label>

                <select
                  v-model="form.categoria"
                  class="requests-input"
                >
                  <option>
                    Evidencias docentes
                  </option>

                  <option>
                    Planificaciones
                  </option>

                  <option>
                    Administrativo
                  </option>
                </select>
              </div>

              <div class="requests-form-group">
                <label class="required">
                  Fecha límite
                </label>

                <input
                  v-model="form.fecha_limite"
                  :min="hoy"
                  type="date"
                  class="requests-input"
                  required
                />
              </div>

              <div class="requests-form-group">
                <label>Prioridad</label>

                <select
                  v-model="form.prioridad"
                  class="requests-input"
                >
                  <option value="normal">
                    Normal
                  </option>

                  <option value="alta">
                    Alta
                  </option>
                </select>
              </div>
            </div>

            <div class="requests-form-group">
              <label class="required">
                Formatos permitidos
              </label>

              <div class="requests-check-grid">
                <label class="requests-check-item">
                  <input
                    v-model="form.formatos"
                    type="checkbox"
                    value="PDF"
                  />
                  PDF
                </label>

                <label class="requests-check-item">
                  <input
                    v-model="form.formatos"
                    type="checkbox"
                    value="DOCX"
                  />
                  DOCX
                </label>

                <label class="requests-check-item">
                  <input
                    v-model="form.formatos"
                    type="checkbox"
                    value="XLSX"
                  />
                  XLSX
                </label>

                <label class="requests-check-item">
                  <input
                    v-model="form.formatos"
                    type="checkbox"
                    value="PNG"
                  />
                  PNG/JPG
                </label>
              </div>
            </div>

            <div class="requests-form-group">
              <label class="required">
                Destinatarios
              </label>

              <div class="requests-radio-group">
                <label class="requests-radio-card">
                  <input
                    v-model="form.modo"
                    type="radio"
                    value="all"
                  />

                  <span>
                    <strong>
                      Todos los docentes
                    </strong>

                    <small>
                      {{
                        textoTodosDocentes
                      }}
                    </small>
                  </span>
                </label>

                <label class="requests-radio-card">
                  <input
                    v-model="form.modo"
                    type="radio"
                    value="selected"
                  />

                  <span>
                    <strong>
                      Docentes seleccionados
                    </strong>

                    <small>
                      Elegir destinatarios específicos.
                    </small>
                  </span>
                </label>
              </div>
            </div>

            <div
              v-if="form.modo === 'selected'"
              class="requests-check-grid requests-teachers"
            >
              <label
                v-for="docente in docentes"
                :key="docente.id_usuario"
                class="requests-check-item"
              >
                <input
                  v-model="form.destinatarios"
                  type="checkbox"
                  :value="docente.id_usuario"
                />

                <span>
                  <strong>
                    {{ docente.nombre }}
                  </strong>

                  <small>
                    {{ docente.alcance }}
                  </small>
                </span>
              </label>
            </div>

            <div
              v-if="errorModal"
              class="requests-alert requests-alert-error"
            >
              {{ errorModal }}
            </div>
          </form>
        </div>

        <footer class="requests-modal-footer">
          <button
            class="requests-btn requests-btn-secondary"
            type="button"
            @click="cerrarModales"
          >
            Cancelar
          </button>

          <button
            form="crear-solicitud-form"
            class="requests-btn requests-btn-primary"
            type="submit"
            :disabled="procesando"
          >
            {{
              procesando
                ? "Creando..."
                : "Crear solicitud"
            }}
          </button>
        </footer>
      </section>
    </div>

    <!-- ================================================= -->
    <!-- CUMPLIMIENTO                                      -->
    <!-- ================================================= -->

    <div
      v-if="modalCumplimiento"
      class="requests-overlay"
      @click.self="cerrarModales"
    >
      <section class="requests-modal requests-modal-lg">
        <header class="requests-modal-head">
          <div>
            <p>CUMPLIMIENTO DOCENTE</p>

            <h2>
              {{ solicitudSeleccionada?.titulo }}
            </h2>
          </div>

          <button
            class="requests-close"
            type="button"
            @click="cerrarModales"
          >
            ×
          </button>
        </header>

        <div class="requests-modal-body">
          <div
            v-if="cargandoCumplimiento"
            class="requests-empty"
          >
            Cargando cumplimiento...
          </div>

          <div
            v-else
            class="requests-table-wrap"
          >
            <table>
              <thead>
                <tr>
                  <th>Docente</th>
                  <th>Alcance</th>
                  <th>Estado</th>
                  <th>Fecha</th>
                  <th>Acción</th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="fila in cumplimiento"
                  :key="fila.id_destinatario"
                >
                  <td>
                    {{ fila.docente }}
                  </td>

                  <td>
                    {{ fila.alcance }}
                  </td>

                  <td>
                    <span
                      class="requests-status"
                      :class="cumplimientoClase(fila.estado)"
                    >
                      {{ cumplimientoTexto(fila.estado) }}
                    </span>
                  </td>

                  <td>
                    {{
                      fila.fecha
                        ? formatearFechaHora(fila.fecha)
                        : "—"
                    }}
                  </td>

                  <td>
                    <button
                      v-if="fila.id_entrega"
                      class="requests-btn requests-btn-soft requests-btn-sm"
                      type="button"
                      @click="abrirEntrega(fila)"
                    >
                      Abrir
                    </button>

                    <span v-else>—</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <footer class="requests-modal-footer">
          <button
            class="requests-btn requests-btn-primary"
            type="button"
            @click="cerrarModales"
          >
            Cerrar
          </button>
        </footer>
      </section>
    </div>

    <!-- ================================================= -->
    <!-- CONFIRMAR CIERRE                                  -->
    <!-- ================================================= -->

    <div
      v-if="modalCerrar"
      class="requests-overlay"
      @click.self="cerrarModales"
    >
      <section class="requests-modal requests-modal-sm">
        <header class="requests-modal-head">
          <div>
            <p>GESTIÓN DE SOLICITUDES</p>
            <h2>Cerrar solicitud</h2>
          </div>
        </header>

        <div class="requests-modal-body">
          <p>
            Los docentes ya no podrán realizar nuevas
            entregas ni enviar correcciones.
            Los documentos existentes se conservarán.
          </p>

          <strong>
            {{ solicitudSeleccionada?.titulo }}
          </strong>
        </div>

        <footer class="requests-modal-footer">
          <button
            class="requests-btn requests-btn-secondary"
            type="button"
            @click="cerrarModales"
          >
            Cancelar
          </button>

          <button
            class="requests-btn requests-btn-primary"
            type="button"
            :disabled="procesando"
            @click="confirmarCerrar"
          >
            Cerrar solicitud
          </button>
        </footer>
      </section>
    </div>

    <!-- ================================================= -->
    <!-- REABRIR                                           -->
    <!-- ================================================= -->

    <div
      v-if="modalReabrir"
      class="requests-overlay"
      @click.self="cerrarModales"
    >
      <section class="requests-modal requests-modal-sm">
        <header class="requests-modal-head">
          <div>
            <p>GESTIÓN DE SOLICITUDES</p>
            <h2>Reabrir solicitud</h2>
          </div>
        </header>

        <div class="requests-modal-body">
          <div class="requests-info">
            Se habilitarán nuevamente las entregas
            pendientes y las correcciones solicitadas.
            Los documentos anteriores se conservarán.
          </div>

          <div class="requests-form-group">
            <label>Solicitud</label>

            <strong>
              {{ solicitudSeleccionada?.titulo }}
            </strong>
          </div>

          <div class="requests-form-group">
            <label class="required">
              Nueva fecha límite
            </label>

            <input
              v-model="nuevaFecha"
              :min="hoy"
              type="date"
              class="requests-input"
              required
            />
          </div>

          <div
            v-if="errorModal"
            class="requests-alert requests-alert-error"
          >
            {{ errorModal }}
          </div>
        </div>

        <footer class="requests-modal-footer">
          <button
            class="requests-btn requests-btn-secondary"
            type="button"
            @click="cerrarModales"
          >
            Cancelar
          </button>

          <button
            class="requests-btn requests-btn-primary"
            type="button"
            :disabled="procesando"
            @click="confirmarReabrir"
          >
            Confirmar reapertura
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
  obtenerSolicitudes,
  obtenerCatalogosSolicitudes,
  crearSolicitud,
  obtenerCumplimiento,
  cerrarSolicitud,
  reabrirSolicitud
} from "../../services/requestsService";

import "../../assets/css/requests.css";

export default {
  name: "RequestsView",

  components: {
    DirectorSidebar,
    DirectorTopbar
  },

  data() {
    return {
      solicitudes: [],
      ciclos: [],
      docentes: [],
      cumplimiento: [],

      cargando: true,
      cargandoCumplimiento: false,
      procesando: false,

      mensaje: "",
      error: "",
      errorModal: "",

      modalCrear: false,
      modalCumplimiento: false,
      modalCerrar: false,
      modalReabrir: false,

      solicitudSeleccionada: null,
      nuevaFecha: "",

      form: {
        titulo: "",
        descripcion: "",
        categoria: "Evidencias docentes",
        fecha_limite: "",
        prioridad: "normal",
        formatos: ["PDF"],
        modo: "all",
        destinatarios: []
      }
    };
  },

  computed: {
    cicloActivo() {
      return this.ciclos.find(
        ciclo => ciclo.estado === "activo"
      ) || null;
    },

    hoy() {
      const fecha = new Date();

      const year = fecha.getFullYear();

      const month = String(
        fecha.getMonth() + 1
      ).padStart(2, "0");

      const day = String(
        fecha.getDate()
      ).padStart(2, "0");

      return `${year}-${month}-${day}`;
    },

    textoTodosDocentes() {
      const cantidad = this.docentes.length;

      if (cantidad === 1) {
        return "Enviar al docente activo.";
      }

      return `Enviar a los ${cantidad} docentes activos.`;
    }
  },

  async mounted() {
    await this.inicializar();
  },

  methods: {
    async inicializar() {
      this.cargando = true;
      this.error = "";

      try {
        const catalogos =
          await obtenerCatalogosSolicitudes();

        this.ciclos = catalogos.ciclos || [];
        this.docentes = catalogos.docentes || [];

        await this.cargarSolicitudes();
      } catch (error) {
        console.error(error);

        this.error =
          error.response?.data?.mensaje ||
          "No fue posible cargar el módulo.";
      } finally {
        this.cargando = false;
      }
    },

    async cargarSolicitudes() {
      const data = await obtenerSolicitudes(
        this.cicloActivo?.id_ciclo
      );

      this.solicitudes =
        data.solicitudes || [];
    },

    resetForm() {
      this.form = {
        titulo: "",
        descripcion: "",
        categoria: "Evidencias docentes",
        fecha_limite: "",
        prioridad: "normal",
        formatos: ["PDF"],
        modo: "all",
        destinatarios: []
      };
    },

    abrirCrear() {
      this.resetForm();
      this.errorModal = "";
      this.modalCrear = true;
    },

    cerrarModales() {
      if (this.procesando) {
        return;
      }

      this.modalCrear = false;
      this.modalCumplimiento = false;
      this.modalCerrar = false;
      this.modalReabrir = false;

      this.solicitudSeleccionada = null;
      this.cumplimiento = [];
      this.errorModal = "";
    },

    async guardarNuevaSolicitud() {
      this.errorModal = "";

      let destinatarios = [];

      if (this.form.modo === "all") {
        destinatarios =
          this.docentes.map(
            docente => docente.id_usuario
          );
      } else {
        destinatarios = [
          ...this.form.destinatarios
        ];
      }

      if (!destinatarios.length) {
        this.errorModal =
          "Seleccione al menos un docente.";
        return;
      }

      if (!this.form.formatos.length) {
        this.errorModal =
          "Seleccione al menos un formato permitido.";
        return;
      }

      if (!this.cicloActivo) {
        this.errorModal =
          "No existe un ciclo activo.";
        return;
      }

      this.procesando = true;

      try {
        const respuesta =
          await crearSolicitud({
            titulo: this.form.titulo,
            descripcion: this.form.descripcion,
            categoria: this.form.categoria,
            prioridad: this.form.prioridad,
            fecha_limite:
              `${this.form.fecha_limite}T23:59:00`,
            id_ciclo:
              this.cicloActivo.id_ciclo,
            destinatarios:
              destinatarios.map(Number),
            formatos:
              this.form.formatos
          });

        this.modalCrear = false;

        this.mensaje =
          respuesta.mensaje;

        await this.cargarSolicitudes();

      } catch (error) {
        console.error(error);

        this.errorModal =
          error.response?.data?.mensaje ||
          "No fue posible crear la solicitud.";

      } finally {
        this.procesando = false;
      }
    },

    async abrirCumplimiento(solicitud) {
      this.solicitudSeleccionada =
        solicitud;

      this.modalCumplimiento = true;
      this.cargandoCumplimiento = true;

      try {
        const data =
          await obtenerCumplimiento(
            solicitud.id_solicitud
          );

        this.cumplimiento =
          data.cumplimiento || [];

      } catch (error) {
        console.error(error);

        this.error =
          error.response?.data?.mensaje ||
          "No fue posible cargar el cumplimiento.";

      } finally {
        this.cargandoCumplimiento = false;
      }
    },

    abrirEntrega(fila) {
      this.$router.push({
        path: "/directora/revision",
        query: {
          entrega: fila.id_entrega
        }
      });
    },

    pedirCerrar(solicitud) {
      this.solicitudSeleccionada =
        solicitud;

      this.modalCerrar = true;
    },

    async confirmarCerrar() {
      this.procesando = true;

      try {
        const respuesta =
          await cerrarSolicitud(
            this.solicitudSeleccionada.id_solicitud
          );

        this.mensaje =
          respuesta.mensaje;

        this.modalCerrar = false;
        this.solicitudSeleccionada = null;

        await this.cargarSolicitudes();

      } catch (error) {
        console.error(error);

        this.errorModal =
          error.response?.data?.mensaje ||
          "No fue posible cerrar la solicitud.";

      } finally {
        this.procesando = false;
      }
    },

    abrirReabrir(solicitud) {
      this.solicitudSeleccionada =
        solicitud;

      const actual =
        String(
          solicitud.fecha_limite || ""
        ).split("T")[0];

      this.nuevaFecha =
        actual >= this.hoy
          ? actual
          : this.hoy;

      this.errorModal = "";
      this.modalReabrir = true;
    },

    async confirmarReabrir() {
      if (!this.nuevaFecha) {
        this.errorModal =
          "Seleccione una nueva fecha límite.";
        return;
      }

      this.procesando = true;

      try {
        const respuesta =
          await reabrirSolicitud(
            this.solicitudSeleccionada.id_solicitud,
            `${this.nuevaFecha}T23:59:00`
          );

        this.mensaje =
          respuesta.mensaje;

        this.modalReabrir = false;
        this.solicitudSeleccionada = null;

        await this.cargarSolicitudes();

      } catch (error) {
        console.error(error);

        this.errorModal =
          error.response?.data?.mensaje ||
          "No fue posible reabrir la solicitud.";

      } finally {
        this.procesando = false;
      }
    },

    estadoTexto(estado) {
      const estados = {
        publicada: "Vigente",
        cerrada: "Cerrada",
        borrador: "Borrador",
        cancelada: "Cancelada"
      };

      return estados[estado] || estado;
    },

    estadoClase(estado) {
      return `requests-status-${estado}`;
    },

    cumplimientoTexto(estado) {
      const estados = {
        pendiente: "Pendiente",
        vencido: "Vencido",
        entregado: "Recibido",
        en_revision: "En revisión",
        aprobado: "Aprobado",
        correccion_solicitada:
          "Corrección solicitada",
        rechazado: "Rechazado"
      };

      return estados[estado] || estado;
    },

    cumplimientoClase(estado) {
      return `requests-status-${estado}`;
    },

    formatearFecha(fecha) {
      if (!fecha) {
        return "—";
      }

      const [year, month, day] =
        String(fecha)
          .split("T")[0]
          .split("-");

      const meses = [
        "ene", "feb", "mar", "abr",
        "may", "jun", "jul", "ago",
        "sep", "oct", "nov", "dic"
      ];

      return (
        `${Number(day)} ` +
        `${meses[Number(month) - 1]} ` +
        `${year}`
      );
    },

    formatearFechaHora(fecha) {
      if (!fecha) {
        return "—";
      }

      return new Intl.DateTimeFormat(
        "es-GT",
        {
          dateStyle: "short",
          timeStyle: "short"
        }
      ).format(
        new Date(fecha)
      );
    }
  }
};
</script>