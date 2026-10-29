<template>
  <div class="director-layout">
    <DirectorSidebar />

    <div class="director-main">
      <DirectorTopbar />

      <main class="director-content">
        <!-- ==================================================
             ENCABEZADO
        =================================================== -->

        <section class="records-page-head">
          <div>
            <p class="records-eyebrow">
              RECUPERACIÓN
            </p>

            <h1>Papelera</h1>

            <p class="records-subtitle">
              Consulte documentos eliminados, restáurelos
              o elimínelos definitivamente.
            </p>
          </div>
        </section>

        <!-- ==================================================
             AVISO
        =================================================== -->

        <div class="trash-warning">
          <span class="trash-warning-icon">
            !
          </span>

          <span>
            La eliminación definitiva también borra
            los archivos y sus versiones almacenadas.
          </span>
        </div>

        <!-- ==================================================
             CICLO HISTÓRICO
        =================================================== -->

        <div
          v-if="ciclo && !ciclo.editable"
          class="records-info"
        >
          Está consultando el ciclo {{ ciclo.anio }}.
          Este ciclo es histórico y está disponible
          únicamente para consulta.
        </div>

        <!-- ==================================================
             ERROR
        =================================================== -->

        <div
          v-if="error"
          class="records-alert records-alert-error"
        >
          {{ error }}
        </div>

        <!-- ==================================================
             TABLA
        =================================================== -->

        <div
          v-if="cargando"
          class="records-empty"
        >
          Cargando papelera...
        </div>

        <section
          v-else
          class="records-table-card"
        >
          <div class="records-table-wrap">
            <table class="trash-table">
              <thead>
                <tr>
                  <th>Registro</th>
                  <th>Origen</th>
                  <th>Eliminado por</th>
                  <th>Fecha</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="documento in documentos"
                  :key="`${documento.tipo}-${documento.id_documento}`"
                >
                  <td>
                    <div class="records-cell-title">
                      {{ documento.titulo }}
                    </div>

                    <div class="records-cell-sub">
                      {{ documento.codigo }}
                    </div>
                  </td>

                  <td>
                    <span class="trash-origin-badge">
                      {{ documento.origen }}
                    </span>
                  </td>

                  <td>
                    {{ documento.eliminado_por }}
                  </td>

                  <td>
                    {{ formatearFechaHora(documento.fecha_papelera) }}
                  </td>

                  <td>
                    <div class="trash-actions">
                      <button
                        type="button"
                        class="records-btn records-btn-soft records-btn-sm"
                        @click="abrirDetalle(documento)"
                      >
                        Ver documento
                      </button>

                      <button
                        v-if="ciclo?.editable"
                        type="button"
                        class="records-btn records-btn-secondary records-btn-sm"
                        @click="abrirRestaurar(documento)"
                      >
                        Restaurar
                      </button>

                      <button
                        v-if="ciclo?.editable"
                        type="button"
                        class="trash-delete-small"
                        @click="abrirEliminar(documento)"
                      >
                        Eliminar
                      </button>
                    </div>
                  </td>
                </tr>

                <tr v-if="!documentos.length">
                  <td
                    colspan="5"
                    class="trash-empty-cell"
                  >
                    <div class="trash-empty">
                      <strong>
                        Papelera vacía
                      </strong>

                      <span>
                        No hay elementos eliminados.
                      </span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>

    <!-- ==================================================
         MODAL · VER DOCUMENTO
    =================================================== -->

    <div
      v-if="modalDetalle"
      class="records-overlay"
      @click.self="cerrarDetalle"
    >
      <section class="records-modal records-modal-lg">
        <header class="records-modal-head">
          <div>
            <p>PAPELERA</p>

            <h2>
              Ver documento
            </h2>
          </div>

          <button
            type="button"
            class="records-close"
            @click="cerrarDetalle"
          >
            ×
          </button>
        </header>

        <div
          v-if="cargandoDetalle"
          class="records-modal-body"
        >
          <div class="records-empty">
            Cargando documento...
          </div>
        </div>

        <div
          v-else-if="detalleDocumento"
          class="records-modal-body"
        >
          <section class="records-detail-grid">
            <div class="records-detail-item">
              <label>
                CÓDIGO
              </label>

              <strong>
                {{ detalleDocumento.codigo }}
              </strong>
            </div>

            <div class="records-detail-item">
              <label>
                TÍTULO
              </label>

              <strong>
                {{ detalleDocumento.titulo }}
              </strong>
            </div>

            <div class="records-detail-item">
              <label>
                ORIGEN
              </label>

              <strong>
                {{ detalleDocumento.origen }}
              </strong>
            </div>

            <div class="records-detail-item">
              <label>
                CATEGORÍA
              </label>

              <strong>
                {{ detalleDocumento.categoria }}
              </strong>
            </div>

            <div class="records-detail-item">
              <label>
                CICLO ESCOLAR
              </label>

              <strong>
                {{ detalleDocumento.ciclo }}
              </strong>
            </div>

            <div class="records-detail-item">
              <label>
                ESTADO
              </label>

              <strong>
                {{ detalleDocumento.estado }}
              </strong>
            </div>

            <div class="records-detail-item">
              <label>
                VERSIÓN ACTUAL
              </label>

              <strong>
                v{{ detalleDocumento.version_actual }}
              </strong>
            </div>

            <div class="records-detail-item">
              <label>
                ELIMINADO POR
              </label>

              <strong>
                {{ detalleDocumento.eliminado_por }}
              </strong>
            </div>

            <div class="records-detail-item">
              <label>
                FECHA DE ELIMINACIÓN
              </label>

              <strong>
                {{
                  formatearFechaHora(
                    detalleDocumento.fecha_papelera
                  )
                }}
              </strong>
            </div>

            <div class="records-detail-item">
              <label>
                ARCHIVO
              </label>

              <strong>
                {{
                  detalleDocumento.archivo?.nombre_archivo
                  || "Sin archivo"
                }}
              </strong>
            </div>
          </section>

          <div class="trash-description">
            <label>
              DESCRIPCIÓN / OBSERVACIONES
            </label>

            <p>
              {{
                detalleDocumento.descripcion
                || "Sin observaciones."
              }}
            </p>
          </div>

          <div class="trash-file-actions">
            <button
              v-if="
                puedePrevisualizar(
                  detalleDocumento.archivo?.tipo_mime
                )
              "
              type="button"
              class="records-btn records-btn-soft"
              @click="verArchivo"
            >
              Ver archivo
            </button>

            <button
              type="button"
              class="records-btn records-btn-secondary"
              @click="descargarArchivo"
            >
              Descargar
            </button>
          </div>

          <h3 class="records-list-title">
            Historial de versiones
          </h3>

          <section class="trash-version-list">
            <article
              v-for="version in detalleDocumento.versiones"
              :key="version.id_version"
              class="trash-version-item"
            >
              <div>
                <strong>
                  Versión {{ version.numero_version }}
                </strong>

                <p>
                  {{ version.nombre_archivo }}
                </p>

                <p>
                  {{
                    formatearFechaHora(
                      version.fecha_subida
                    )
                  }}
                </p>

                <p v-if="version.motivo">
                  Motivo:
                  {{ version.motivo }}
                </p>
              </div>
            </article>

            <p
              v-if="!detalleDocumento.versiones?.length"
              class="records-muted"
            >
              No hay versiones registradas.
            </p>
          </section>
        </div>

        <footer class="records-modal-footer">
          <button
            type="button"
            class="records-btn records-btn-secondary"
            @click="cerrarDetalle"
          >
            Cerrar
          </button>
        </footer>
      </section>
    </div>

    <!-- ==================================================
         MODAL · RESTAURAR
    =================================================== -->

    <div
      v-if="modalRestaurar"
      class="records-overlay"
      @click.self="cerrarRestaurar"
    >
      <section class="records-modal trash-confirm-modal">
        <header class="records-modal-head">
          <div>
            <p>
              CONFIRMAR ACCIÓN
            </p>

            <h2>
              Restaurar documento
            </h2>
          </div>

          <button
            type="button"
            class="records-close"
            @click="cerrarRestaurar"
          >
            ×
          </button>
        </header>

        <div class="records-modal-body">
          <p class="trash-confirm-text">
            ¿Desea restaurar
            <strong>
              {{ documentoSeleccionado?.titulo }}
            </strong>
            ?
          </p>

          <div class="trash-restore-info">
            El registro volverá a su módulo de origen.
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
            :disabled="procesando"
            @click="cerrarRestaurar"
          >
            Cancelar
          </button>

          <button
            type="button"
            class="records-btn records-btn-primary"
            :disabled="procesando"
            @click="confirmarRestaurar"
          >
            {{
              procesando
                ? "Restaurando..."
                : "Confirmar"
            }}
          </button>
        </footer>
      </section>
    </div>

    <!-- ==================================================
         MODAL · ELIMINAR DEFINITIVAMENTE
    =================================================== -->

    <div
      v-if="modalEliminar"
      class="records-overlay"
      @click.self="cerrarEliminar"
    >
      <section class="records-modal trash-confirm-modal">
        <header class="records-modal-head">
          <div>
            <p>
              CONFIRMAR ACCIÓN
            </p>

            <h2>
              Eliminar definitivamente
            </h2>
          </div>

          <button
            type="button"
            class="records-close"
            @click="cerrarEliminar"
          >
            ×
          </button>
        </header>

        <div class="records-modal-body">
          <p class="trash-confirm-text">
            Está a punto de eliminar definitivamente
            <strong>
              {{ documentoSeleccionado?.titulo }}
            </strong>.
          </p>

          <div class="trash-delete-warning">
            Esta acción eliminará el registro,
            sus versiones y los archivos almacenados.
            No podrá deshacerse.
          </div>

          <div class="records-form-group">
            <label>
              Escriba
              <strong>ELIMINAR</strong>
              para confirmar
            </label>

            <input
              v-model.trim="confirmacionEliminar"
              type="text"
              class="records-input"
              autocomplete="off"
              placeholder="ELIMINAR"
            />
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
            :disabled="procesando"
            @click="cerrarEliminar"
          >
            Cancelar
          </button>

          <button
            type="button"
            class="trash-delete-button"
            :disabled="
              procesando ||
              confirmacionEliminar !== 'ELIMINAR'
            "
            @click="confirmarEliminar"
          >
            {{
              procesando
                ? "Eliminando..."
                : "Eliminar definitivamente"
            }}
          </button>
        </footer>
      </section>
    </div>

    <!-- ==================================================
         TOAST
    =================================================== -->

    <div
      v-if="mensaje"
      class="trash-toast"
    >
      <span class="trash-toast-check">
        ✓
      </span>

      <span class="trash-toast-text">
        {{ mensaje }}
      </span>

      <button
        type="button"
        class="trash-toast-close"
        @click="cerrarToast"
      >
        ×
      </button>
    </div>
  </div>
</template>


<script>
import DirectorSidebar from "../../components/layout/DirectorSidebar.vue";
import DirectorTopbar from "../../components/layout/DirectorTopbar.vue";

import {
  obtenerPapelera,
  obtenerDetallePapelera,
  restaurarDocumentoPapelera,
  verDocumentoPapelera,
  descargarDocumentoPapelera,
  eliminarDocumentoPapelera
} from "../../services/papeleraService";

import "../../assets/css/expedientes.css";
import "../../assets/css/papelera.css";


export default {
  name: "TrashView",

  components: {
    DirectorSidebar,
    DirectorTopbar
  },


  data() {
    return {
      ciclo: null,

      documentos: [],

      cargando: true,
      cargandoDetalle: false,
      procesando: false,

      mensaje: "",
      error: "",
      errorModal: "",

      modalDetalle: false,
      modalRestaurar: false,
      modalEliminar: false,

      detalleDocumento: null,
      documentoSeleccionado: null,

      confirmacionEliminar: "",

      temporizadorToast: null
    };
  },


  async mounted() {
    window.addEventListener(
      "sgad-cycle-changed",
      this.manejarCambioCiclo
    );

    await this.cargarPapelera();
  },


  beforeUnmount() {
    window.removeEventListener(
      "sgad-cycle-changed",
      this.manejarCambioCiclo
    );

    if (this.temporizadorToast) {
      clearTimeout(
        this.temporizadorToast
      );
    }
  },


  methods: {
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


    async manejarCambioCiclo() {
      this.cerrarTodosLosModales();

      await this.cargarPapelera();
    },


    cerrarTodosLosModales() {
      this.modalDetalle = false;
      this.modalRestaurar = false;
      this.modalEliminar = false;

      this.detalleDocumento = null;
      this.documentoSeleccionado = null;

      this.confirmacionEliminar = "";
      this.errorModal = "";
    },


    mostrarToast(texto) {
      this.mensaje =
        texto || "";

      if (this.temporizadorToast) {
        clearTimeout(
          this.temporizadorToast
        );
      }

      if (this.mensaje) {
        this.temporizadorToast =
          setTimeout(() => {
            this.mensaje = "";
            this.temporizadorToast = null;
          }, 4000);
      }
    },


    cerrarToast() {
      this.mensaje = "";

      if (this.temporizadorToast) {
        clearTimeout(
          this.temporizadorToast
        );

        this.temporizadorToast = null;
      }
    },


    async cargarPapelera() {
      this.cargando = true;
      this.error = "";

      try {
        const idCiclo =
          this.obtenerIdCicloSeleccionado();

        const data =
          await obtenerPapelera(
            idCiclo
          );

        this.ciclo =
          data.ciclo || null;

        this.documentos =
          data.documentos || [];

      } catch (error) {
        console.error(error);

        this.error =
          error.response?.data?.mensaje ||
          "No fue posible cargar la papelera.";

      } finally {
        this.cargando = false;
      }
    },


    async abrirDetalle(
      documento
    ) {
      this.documentoSeleccionado =
        documento;

      this.detalleDocumento = null;

      this.modalDetalle = true;
      this.cargandoDetalle = true;
      this.errorModal = "";

      try {
        const data =
          await obtenerDetallePapelera(
            documento.id_documento
          );

        this.detalleDocumento =
          data.documento;

      } catch (error) {
        console.error(error);

        this.error =
          error.response?.data?.mensaje ||
          "No fue posible cargar el documento.";

        this.modalDetalle = false;

      } finally {
        this.cargandoDetalle = false;
      }
    },


    cerrarDetalle() {
      this.modalDetalle = false;
      this.detalleDocumento = null;
      this.documentoSeleccionado = null;
    },


    abrirRestaurar(
      documento
    ) {
      this.documentoSeleccionado =
        documento;

      this.errorModal = "";
      this.modalRestaurar = true;
    },


    cerrarRestaurar() {
      if (this.procesando) {
        return;
      }

      this.modalRestaurar = false;
      this.documentoSeleccionado = null;
      this.errorModal = "";
    },


    async confirmarRestaurar() {
      if (!this.documentoSeleccionado) {
        return;
      }

      this.procesando = true;
      this.errorModal = "";

      try {
        const respuesta =
          await restaurarDocumentoPapelera(
            this.documentoSeleccionado
              .id_documento
          );

        this.mostrarToast(
          respuesta.mensaje
        );

        this.modalRestaurar = false;
        this.documentoSeleccionado = null;

        await this.cargarPapelera();

      } catch (error) {
        console.error(error);

        this.errorModal =
          error.response?.data?.mensaje ||
          "No fue posible restaurar el documento.";

      } finally {
        this.procesando = false;
      }
    },


    abrirEliminar(
      documento
    ) {
      this.documentoSeleccionado =
        documento;

      this.confirmacionEliminar = "";
      this.errorModal = "";

      this.modalEliminar = true;
    },


    cerrarEliminar() {
      if (this.procesando) {
        return;
      }

      this.modalEliminar = false;

      this.documentoSeleccionado = null;

      this.confirmacionEliminar = "";
      this.errorModal = "";
    },


    async confirmarEliminar() {
      if (!this.documentoSeleccionado) {
        return;
      }

      if (
        this.confirmacionEliminar !==
        "ELIMINAR"
      ) {
        this.errorModal =
          "Escriba ELIMINAR para confirmar.";

        return;
      }

      this.procesando = true;
      this.errorModal = "";

      try {
        const respuesta =
          await eliminarDocumentoPapelera(
            this.documentoSeleccionado
              .id_documento
          );

        this.mostrarToast(
          respuesta.mensaje
        );

        this.modalEliminar = false;

        this.documentoSeleccionado = null;

        this.confirmacionEliminar = "";

        await this.cargarPapelera();

      } catch (error) {
        console.error(error);

        this.errorModal =
          error.response?.data?.mensaje ||
          "No fue posible eliminar el documento.";

      } finally {
        this.procesando = false;
      }
    },


    puedePrevisualizar(
      tipoMime
    ) {
      return [
        "application/pdf",
        "image/jpeg",
        "image/png"
      ].includes(
        tipoMime
      );
    },


    async verArchivo() {
      if (!this.detalleDocumento) {
        return;
      }

      try {
        await verDocumentoPapelera(
          this.detalleDocumento
            .id_documento
        );

      } catch (error) {
        console.error(error);

        this.error =
          error.response?.data?.mensaje ||
          "No fue posible abrir el archivo.";
      }
    },


    async descargarArchivo() {
      if (!this.detalleDocumento) {
        return;
      }

      try {
        await descargarDocumentoPapelera(
          this.detalleDocumento
            .id_documento
        );

      } catch (error) {
        console.error(error);

        this.error =
          "No fue posible descargar el archivo.";
      }
    },


    formatearFechaHora(
      fecha
    ) {
      if (!fecha) {
        return "—";
      }

      let fechaUtc =
        String(fecha);

      const tieneZonaHoraria =
        fechaUtc.endsWith("Z") ||
        /[+-]\d{2}:\d{2}$/.test(
          fechaUtc
        );

      if (!tieneZonaHoraria) {
        fechaUtc += "Z";
      }

      const valor =
        new Date(
          fechaUtc
        );

      if (
        Number.isNaN(
          valor.getTime()
        )
      ) {
        return fecha;
      }

      return valor.toLocaleString(
        "es-GT",
        {
          timeZone:
            "America/Guatemala",

          dateStyle:
            "short",

          timeStyle:
            "short"
        }
      );
    }
  }
};
</script>