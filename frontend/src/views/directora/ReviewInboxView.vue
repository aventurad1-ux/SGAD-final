<template>
  <div class="director-layout">
    <DirectorSidebar />

    <div class="director-main">
      <DirectorTopbar />

      <main class="director-content">
        <section class="review-header">
          <div>
            <p class="review-eyebrow">
              SEGUIMIENTO DOCUMENTAL
            </p>

            <h1>
              Bandeja de revisión
            </h1>

            <p>
              Abra el archivo antes de emitir un dictamen.
            </p>
          </div>
        </section>

        <section class="review-card">
          <div class="review-filters">
            <input
              v-model="busqueda"
              type="text"
              placeholder="Buscar solicitud, docente o código..."
            />

            <select v-model="estadoSeleccionado">
              <option value="">
                Todos los estados
              </option>

              <option value="entregado">
                Recibido
              </option>

              <option value="en_revision">
                En revisión
              </option>

              <option value="aprobado">
                Aprobado
              </option>

              <option value="correccion_solicitada">
                Corrección solicitada
              </option>
            </select>

            <select v-model="docenteSeleccionado">
              <option value="">
                Todos los docentes
              </option>

              <option
                v-for="docente in docentesDisponibles"
                :key="docente"
                :value="docente"
              >
                {{ docente }}
              </option>
            </select>
          </div>

          <div
            v-if="mensajeExito"
            class="review-success"
          >
            {{ mensajeExito }}
          </div>

          <div
            v-if="mensajeError"
            class="review-error"
          >
            {{ mensajeError }}
          </div>

          <div
            v-if="cargando"
            class="review-loading"
          >
            Cargando entregas...
          </div>

          <div
            v-else
            class="review-table-wrapper"
          >
            <table class="review-table">
              <thead>
                <tr>
                  <th>Solicitud</th>
                  <th>Docente</th>
                  <th>Fecha</th>
                  <th>Estado</th>
                  <th>Acción</th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="entrega in entregasFiltradas"
                  :key="entrega.id"
                >
                  <td>
                    <strong>
                      {{ entrega.solicitud }}
                    </strong>

                    <span class="request-code">
                      {{ entrega.codigo }}
                    </span>
                  </td>

                  <td>
                    {{ entrega.docente }}
                  </td>

                  <td>
                    {{ entrega.fecha || "Sin fecha" }}
                  </td>

                  <td>
                    <span
                      class="status-badge"
                      :class="estadoClase(entrega.estado)"
                    >
                      {{ estadoTexto(entrega.estado) }}
                    </span>
                  </td>

                  <td>
                    <button
                      type="button"
                      class="review-button"
                      @click="abrirRevision(entrega)"
                    >
                      Revisar
                    </button>
                  </td>
                </tr>

                <tr v-if="entregasFiltradas.length === 0">
                  <td
                    colspan="5"
                    class="empty-state"
                  >
                    No se encontraron entregas.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>

    <!-- MODAL DE REVISIÓN -->
    <div
      v-if="mostrarModalRevision && entregaSeleccionada"
      class="modal-overlay"
      @click.self="cerrarRevision"
    >
      <section class="review-modal">
        <header class="review-modal-header">
          <div>
            <p>
              REVISIÓN DOCUMENTAL
            </p>

            <h2>
              {{ entregaSeleccionada.codigo }}
            </h2>
          </div>

          <button
            type="button"
            class="modal-close"
            @click="cerrarRevision"
          >
            ×
          </button>
        </header>

        <div class="review-detail-grid">
          <div class="review-detail-item">
            <span>Solicitud</span>

            <strong>
              {{ entregaSeleccionada.solicitud }}
            </strong>
          </div>

          <div class="review-detail-item">
            <span>Docente</span>

            <strong>
              {{ entregaSeleccionada.docente }}
            </strong>
          </div>

          <div class="review-detail-item">
            <span>Fecha de entrega</span>

            <strong>
              {{ entregaSeleccionada.fecha || "Sin fecha" }}
            </strong>
          </div>

          <div class="review-detail-item">
            <span>Estado</span>

            <strong>
              {{ estadoTexto(entregaSeleccionada.estado) }}
            </strong>
          </div>

          <div class="review-detail-item">
            <span>Archivo</span>

            <strong>
              {{ entregaSeleccionada.archivo || "Sin archivo" }}
            </strong>
          </div>

          <div class="review-detail-item">
            <span>Versión</span>

            <strong>
              v{{ entregaSeleccionada.version || 1 }}
            </strong>
          </div>
        </div>

        <footer class="review-modal-footer">
          <button
            type="button"
            class="modal-secondary-button"
            @click="cerrarRevision"
          >
            Cerrar
          </button>

          <button
            v-if="puedeDictaminar"
            type="button"
            class="modal-warning-button"
            :disabled="procesando"
            @click="abrirCorreccion"
          >
            Solicitar corrección
          </button>

          <button
            v-if="puedeDictaminar"
            type="button"
            class="modal-primary-button"
            :disabled="procesando"
            @click="confirmarAprobacion"
          >
            {{ procesando ? "Procesando..." : "Aprobar" }}
          </button>
        </footer>
      </section>
    </div>

    <!-- MODAL PARA SOLICITAR CORRECCIÓN -->
    <div
      v-if="mostrarModalCorreccion && entregaSeleccionada"
      class="modal-overlay"
      @click.self="cerrarCorreccion"
    >
      <section class="correction-modal">
        <header class="review-modal-header">
          <div>
            <p>
              REVISIÓN DOCUMENTAL
            </p>

            <h2>
              Solicitar corrección
            </h2>
          </div>

          <button
            type="button"
            class="modal-close"
            @click="cerrarCorreccion"
          >
            ×
          </button>
        </header>

        <div class="correction-form">
          <p class="correction-document">
            <strong>
              {{ entregaSeleccionada.solicitud }}
            </strong>

            <span>
              {{ entregaSeleccionada.docente }}
            </span>
          </p>

          <label for="observaciones">
            Motivo e instrucciones para el docente
          </label>

          <textarea
            id="observaciones"
            v-model="observacionesCorreccion"
            placeholder="Explique claramente qué debe corregir el docente..."
            minlength="8"
          ></textarea>

          <small>
            Escriba al menos 8 caracteres.
          </small>

          <p
            v-if="errorCorreccion"
            class="correction-error"
          >
            {{ errorCorreccion }}
          </p>
        </div>

        <footer class="review-modal-footer">
          <button
            type="button"
            class="modal-secondary-button"
            :disabled="procesando"
            @click="cerrarCorreccion"
          >
            Cancelar
          </button>

          <button
            type="button"
            class="modal-warning-button"
            :disabled="procesando"
            @click="enviarCorreccion"
          >
            {{
              procesando
                ? "Enviando..."
                : "Enviar corrección"
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
  obtenerBandejaRevision,
  aprobarEntrega,
  solicitarCorreccion
} from "../../services/reviewService";

import "../../assets/css/review-inbox.css";

export default {
  name: "ReviewInboxView",

  components: {
    DirectorSidebar,
    DirectorTopbar
  },

  data() {
    return {
      busqueda: "",
      estadoSeleccionado: "",
      docenteSeleccionado: "",

      entregas: [],

      cargando: false,
      procesando: false,

      mensajeError: "",
      mensajeExito: "",

      entregaSeleccionada: null,

      mostrarModalRevision: false,
      mostrarModalCorreccion: false,

      observacionesCorreccion: "",
      errorCorreccion: ""
    };
  },

  computed: {
    docentesDisponibles() {
      const docentes = this.entregas
        .map((entrega) => entrega.docente)
        .filter(Boolean);

      return [...new Set(docentes)].sort();
    },

    entregasFiltradas() {
      const texto =
        this.busqueda.trim().toLowerCase();

      return this.entregas.filter((entrega) => {
        const solicitud =
          entrega.solicitud?.toLowerCase() || "";

        const docente =
          entrega.docente?.toLowerCase() || "";

        const codigo =
          entrega.codigo?.toLowerCase() || "";

        const coincideBusqueda =
          solicitud.includes(texto) ||
          docente.includes(texto) ||
          codigo.includes(texto);

        const coincideEstado =
          !this.estadoSeleccionado ||
          entrega.estado ===
            this.estadoSeleccionado;

        const coincideDocente =
          !this.docenteSeleccionado ||
          entrega.docente ===
            this.docenteSeleccionado;

        return (
          coincideBusqueda &&
          coincideEstado &&
          coincideDocente
        );
      });
    },

    puedeDictaminar() {
      if (!this.entregaSeleccionada) {
        return false;
      }

      return [
        "entregado",
        "en_revision"
      ].includes(
        this.entregaSeleccionada.estado
      );
    }
  },

  async mounted() {
    await this.cargarEntregas();
  },

  methods: {
    async cargarEntregas() {
      this.cargando = true;
      this.mensajeError = "";

      try {
        const data =
          await obtenerBandejaRevision();

        this.entregas =
          data.entregas.map((entrega) => ({
            id: entrega.id_entrega,

            id_version_entrega:
              entrega.id_version_entrega,

            solicitud:
              entrega.solicitud,

            codigo:
              entrega.codigo,

            docente:
              entrega.docente,

            fecha:
              entrega.fecha,

            estado:
              entrega.estado,

            archivo:
              entrega.archivo,

            version:
              entrega.version
          }));
      } catch (error) {
        console.error(
          "Error al cargar bandeja:",
          error
        );

        this.mensajeError =
          error.response?.data?.mensaje ||
          error.response?.data?.message ||
          "No fue posible cargar la bandeja de revisión.";
      } finally {
        this.cargando = false;
      }
    },

    estadoClase(estado) {
      if (estado === "aprobado") {
        return "status-approved";
      }

      if (
        estado === "correccion_solicitada" ||
        estado === "rechazado"
      ) {
        return "status-correction";
      }

      return "status-pending";
    },

    estadoTexto(estado) {
      const estados = {
        pendiente: "Pendiente",
        entregado: "Recibido",
        en_revision: "En revisión",
        correccion_solicitada:
          "Corrección solicitada",
        aprobado: "Aprobado",
        rechazado: "Rechazado"
      };

      return estados[estado] || estado;
    },

    abrirRevision(entrega) {
      this.entregaSeleccionada = {
        ...entrega
      };

      this.mensajeError = "";
      this.mensajeExito = "";

      this.mostrarModalRevision = true;
    },

    cerrarRevision() {
      if (this.procesando) {
        return;
      }

      this.mostrarModalRevision = false;
      this.entregaSeleccionada = null;
    },

    abrirCorreccion() {
      this.observacionesCorreccion = "";
      this.errorCorreccion = "";

      this.mostrarModalRevision = false;
      this.mostrarModalCorreccion = true;
    },

    cerrarCorreccion() {
      if (this.procesando) {
        return;
      }

      this.mostrarModalCorreccion = false;
      this.observacionesCorreccion = "";
      this.errorCorreccion = "";

      this.mostrarModalRevision = true;
    },

    async confirmarAprobacion() {
      if (
        !this.entregaSeleccionada ||
        this.procesando
      ) {
        return;
      }

      const confirmar = window.confirm(
        "¿Desea aprobar esta entrega?"
      );

      if (!confirmar) {
        return;
      }

      this.procesando = true;
      this.mensajeError = "";
      this.mensajeExito = "";

      try {
        const respuesta =
          await aprobarEntrega(
            this.entregaSeleccionada.id
          );

        this.mensajeExito =
          respuesta.mensaje ||
          "Entrega aprobada correctamente.";

        this.mostrarModalRevision = false;
        this.entregaSeleccionada = null;

        await this.cargarEntregas();
      } catch (error) {
        console.error(
          "Error al aprobar entrega:",
          error
        );

        this.mensajeError =
          error.response?.data?.mensaje ||
          error.response?.data?.message ||
          "No fue posible aprobar la entrega.";
      } finally {
        this.procesando = false;
      }
    },

    async enviarCorreccion() {
      this.errorCorreccion = "";

      const observaciones =
        this.observacionesCorreccion.trim();

      if (observaciones.length < 8) {
        this.errorCorreccion =
          "Las observaciones deben tener al menos 8 caracteres.";

        return;
      }

      if (
        !this.entregaSeleccionada ||
        this.procesando
      ) {
        return;
      }

      this.procesando = true;
      this.mensajeError = "";
      this.mensajeExito = "";

      try {
        const respuesta =
          await solicitarCorreccion(
            this.entregaSeleccionada.id,
            observaciones
          );

        this.mensajeExito =
          respuesta.mensaje ||
          "Corrección solicitada correctamente.";

        this.mostrarModalCorreccion = false;

        this.observacionesCorreccion = "";
        this.entregaSeleccionada = null;

        await this.cargarEntregas();
      } catch (error) {
        console.error(
          "Error al solicitar corrección:",
          error
        );

        this.errorCorreccion =
          error.response?.data?.mensaje ||
          error.response?.data?.message ||
          "No fue posible solicitar la corrección.";
      } finally {
        this.procesando = false;
      }
    }
  }
};
</script>