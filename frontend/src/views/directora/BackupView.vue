<template>
  <div class="backup-page">
    <DirectorSidebar />

    <main class="backup-main">
      <DirectorTopbar />

      <section class="backup-content">
        <div class="backup-heading">
          <span class="backup-eyebrow">
            SEGURIDAD
          </span>

          <h1>
            Copias de seguridad
          </h1>

          <p>
            Proteja la base de datos y los
            documentos almacenados en SGAD.
          </p>
        </div>

        <div
          v-if="mensaje"
          class="backup-alert backup-alert-success"
        >
          {{ mensaje }}
        </div>

        <div
          v-if="error"
          class="backup-alert backup-alert-error"
        >
          {{ error }}
        </div>

        <div class="backup-actions">
          <article class="backup-card">
            <div class="backup-card-icon">
              ↓
            </div>

            <h2>
              Crear copia de seguridad
            </h2>

            <p>
              Genera un respaldo completo de
              PostgreSQL y de los documentos
              almacenados por SGAD.
            </p>

            <button
              type="button"
              class="backup-primary-button"
              :disabled="generando"
              @click="crearRespaldo"
            >
              {{
                generando
                  ? "Generando respaldo..."
                  : "Crear copia de seguridad"
              }}
            </button>
          </article>

          <article class="backup-card">
            <div class="backup-card-icon">
              ↑
            </div>

            <div class="backup-card-title-row">
              <h2>
                Restaurar copia
              </h2>

              <span class="backup-coming">
                Próximamente
              </span>
            </div>

            <p>
              La restauración estará disponible
              cuando se configure el procedimiento
              seguro de recuperación de PostgreSQL
              y archivos institucionales.
            </p>

            <button
              type="button"
              class="backup-secondary-button"
              disabled
            >
              Seleccionar respaldo
            </button>
          </article>
        </div>

        <section class="backup-info">
          <h2>
            Contenido protegido
          </h2>

          <div class="backup-info-grid">
            <div class="backup-info-item">
              <span>
                BASE DE DATOS
              </span>

              <strong>
                PostgreSQL
              </strong>
            </div>

            <div class="backup-info-item">
              <span>
                ARCHIVOS
              </span>

              <strong>
                Expedientes y documentos
              </strong>
            </div>

            <div class="backup-info-item">
              <span>
                ÚLTIMO RESPALDO
              </span>

              <strong>
                {{ ultimoRespaldo }}
              </strong>
            </div>

            <div class="backup-info-item">
              <span>
                RESPALDOS REGISTRADOS
              </span>

              <strong>
                {{ respaldos.length }}
              </strong>
            </div>
          </div>
        </section>

        <section class="backup-history">
          <div class="backup-history-header">
            <div>
              <span class="backup-eyebrow">
                HISTORIAL
              </span>

              <h2>
                Copias generadas
              </h2>
            </div>

            <button
              type="button"
              class="backup-refresh-button"
              :disabled="cargando"
              @click="cargarRespaldos"
            >
              Actualizar
            </button>
          </div>

          <div
            v-if="cargando"
            class="backup-empty"
          >
            Cargando respaldos...
          </div>

          <div
            v-else-if="respaldos.length === 0"
            class="backup-empty"
          >
            Todavía no se han generado
            copias de seguridad.
          </div>

          <div
            v-else
            class="backup-table-wrapper"
          >
            <table class="backup-table">
              <thead>
                <tr>
                  <th>
                    Archivo
                  </th>

                  <th>
                    Fecha
                  </th>

                  <th>
                    Tamaño
                  </th>

                  <th>
                    Responsable
                  </th>

                  <th>
                    Estado
                  </th>

                  <th>
                    Acción
                  </th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="respaldo in respaldos"
                  :key="respaldo.id_respaldo"
                >
                  <td>
                    <strong>
                      {{
                        respaldo.nombre ||
                        "Sin archivo"
                      }}
                    </strong>

                    <small>
                      {{ respaldo.tipo }}
                    </small>
                  </td>

                  <td>
                    {{
                      formatearFecha(
                        respaldo.fecha
                      )
                    }}
                  </td>

                  <td>
                    {{
                      formatearTamano(
                        respaldo.tamano
                      )
                    }}
                  </td>

                  <td>
                    {{
                      respaldo.responsable ||
                      "No disponible"
                    }}
                  </td>

                  <td>
                    <span
                      class="backup-status"
                      :class="
                        claseEstado(
                          respaldo.estado
                        )
                      "
                    >
                      {{ respaldo.estado }}
                    </span>
                  </td>

                  <td>
                    <button
                      v-if="
                        respaldo.estado ===
                        'Completado' &&
                        respaldo.nombre
                      "
                      type="button"
                      class="backup-download-button"
                      @click="
                        descargar(
                          respaldo.nombre
                        )
                      "
                    >
                      Descargar
                    </button>

                    <span
                      v-else
                      class="backup-unavailable"
                    >
                      No disponible
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </section>
    </main>
  </div>
</template>


<script>
import DirectorSidebar
  from "../../components/layout/DirectorSidebar.vue";

import DirectorTopbar
  from "../../components/layout/DirectorTopbar.vue";

import {
  obtenerRespaldos,
  generarRespaldo,
  descargarRespaldo
} from "../../services/backupService";

import "./backup.css";


export default {
  name: "BackupView",

  components: {
    DirectorSidebar,
    DirectorTopbar
  },

  data() {
    return {
      respaldos: [],
      cargando: false,
      generando: false,
      mensaje: "",
      error: ""
    };
  },

  computed: {
    ultimoRespaldo() {
      if (!this.respaldos.length) {
        return "Sin respaldos";
      }

      return this.formatearFecha(
        this.respaldos[0].fecha
      );
    }
  },

  mounted() {
    this.cargarRespaldos();
  },

  methods: {
    limpiarMensajes() {
      this.mensaje = "";
      this.error = "";
    },

    async cargarRespaldos() {
      this.cargando = true;
      this.error = "";

      try {
        const data =
          await obtenerRespaldos();

        this.respaldos =
          data.respaldos || [];
      } catch (error) {
        console.error(
          "ERROR RESPALDOS:",
          error
        );

        this.error =
          error.response?.data?.mensaje ||
          "No fue posible cargar el historial de respaldos.";
      } finally {
        this.cargando = false;
      }
    },

    async crearRespaldo() {
      if (this.generando) {
        return;
      }

      this.limpiarMensajes();
      this.generando = true;

      try {
        const data =
          await generarRespaldo();

        this.mensaje =
          data.mensaje ||
          "Respaldo generado correctamente.";

        await this.cargarRespaldos();
      } catch (error) {
        console.error(
          "ERROR GENERANDO RESPALDO:",
          error
        );

        this.error =
          error.response?.data?.mensaje ||
          "No fue posible generar la copia de seguridad.";
      } finally {
        this.generando = false;
      }
    },

    async descargar(nombre) {
      this.limpiarMensajes();

      try {
        await descargarRespaldo(
          nombre
        );

        this.mensaje =
          "Descarga del respaldo iniciada.";
      } catch (error) {
        console.error(
          "ERROR DESCARGANDO RESPALDO:",
          error
        );

        this.error =
          error.response?.data?.mensaje ||
          "No fue posible descargar el respaldo.";
      }
    },

    formatearFecha(fecha) {
      if (!fecha) {
        return "No disponible";
      }

      const valor = new Date(fecha);

      if (
        Number.isNaN(
          valor.getTime()
        )
      ) {
        return "No disponible";
      }

      return valor.toLocaleString(
        "es-GT",
        {
          dateStyle: "medium",
          timeStyle: "short"
        }
      );
    },

    formatearTamano(bytes) {
      if (
        bytes === null ||
        bytes === undefined
      ) {
        return "No disponible";
      }

      const numero =
        Number(bytes);

      if (
        Number.isNaN(numero)
      ) {
        return "No disponible";
      }

      if (numero < 1024) {
        return `${numero} B`;
      }

      if (
        numero <
        1024 * 1024
      ) {
        return `${(
          numero / 1024
        ).toFixed(1)} KB`;
      }

      if (
        numero <
        1024 * 1024 * 1024
      ) {
        return `${(
          numero /
          (1024 * 1024)
        ).toFixed(1)} MB`;
      }

      return `${(
        numero /
        (1024 * 1024 * 1024)
      ).toFixed(2)} GB`;
    },

    claseEstado(estado) {
      if (
        estado ===
        "Completado"
      ) {
        return "backup-status-success";
      }

      if (
        estado ===
        "Fallido"
      ) {
        return "backup-status-error";
      }

      return "backup-status-progress";
    }
  }
};
</script>