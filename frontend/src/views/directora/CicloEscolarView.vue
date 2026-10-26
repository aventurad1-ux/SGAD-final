<template>
  <div class="director-layout">
    <DirectorSidebar />

    <div class="director-main">
      <DirectorTopbar />

      <main class="director-content">
        <!-- ==========================================
             ENCABEZADO
        =========================================== -->

        <section class="cycle-page-head">
          <div>
            <p class="cycle-eyebrow">
              ESTRUCTURA ESCOLAR
            </p>

            <h1>Ciclo escolar</h1>

            <p>
              Administre la organización y los responsables
              de cada ciclo.
            </p>
          </div>

          <div class="cycle-page-actions">
            <button
              v-if="ciclo?.editable"
              type="button"
              class="cycle-btn cycle-btn-secondary"
              @click="abrirAgregarSeccion"
            >
              Agregar sección
            </button>

            <button
              type="button"
              class="cycle-btn cycle-btn-primary"
              @click="abrirCrearCiclo"
            >
              Crear ciclo
            </button>
          </div>
        </section>

        <!-- ==========================================
             MENSAJES
        =========================================== -->

        <div
          v-if="mensaje"
          class="cycle-alert cycle-alert-success"
        >
          {{ mensaje }}
        </div>

        <div
          v-if="error"
          class="cycle-alert cycle-alert-error"
        >
          {{ error }}
        </div>

        <!-- ==========================================
             SELECTOR DE CICLO
        =========================================== -->

        <section class="cycle-selector-card">
          <div>
            <span>
              Ciclo consultado
            </span>

            <select
              v-model="cicloSeleccionadoId"
              class="cycle-input cycle-selector"
              @change="cambiarCiclo"
            >
              <option
                v-for="item in ciclos"
                :key="item.id_ciclo"
                :value="String(item.id_ciclo)"
              >
                {{
                  item.estado === "activo"
                    ? `${item.anio} · Actual`
                    : `${item.anio} · Histórico`
                }}
              </option>
            </select>
          </div>
        </section>

        <!-- ==========================================
             CICLO ACTUAL
        =========================================== -->

        <article
          v-if="ciclo"
          class="cycle-main-card"
        >
          <div class="cycle-card-head">
            <div>
              <h2>
                Ciclo {{ ciclo.anio }}
              </h2>

              <p>
                {{ formatearFecha(ciclo.fecha_inicio) }}
                al
                {{ formatearFecha(ciclo.fecha_fin) }}
              </p>
            </div>

            <div class="cycle-card-actions">
              <span
                class="cycle-badge"
                :class="
                  ciclo.estado === 'activo'
                    ? 'cycle-badge-success'
                    : 'cycle-badge-neutral'
                "
              >
                {{
                  ciclo.estado === "activo"
                    ? "Activo"
                    : "Cerrado"
                }}
              </span>

              <button
                v-if="ciclo.editable"
                type="button"
                class="cycle-btn cycle-btn-warning cycle-btn-sm"
                @click="abrirCerrarCiclo"
              >
                Cerrar ciclo
              </button>
            </div>
          </div>

          <div
            class="cycle-status-info"
            :class="
              ciclo.editable
                ? 'cycle-status-success'
                : 'cycle-status-neutral'
            "
          >
            <span class="cycle-status-icon">
              i
            </span>

            <span>
              {{
                ciclo.editable
                  ? "Este ciclo permite matrículas, documentos y cambios de estructura."
                  : "Este ciclo es histórico y se encuentra disponible únicamente para consulta."
              }}
            </span>
          </div>
        </article>

        <!-- ==========================================
             SECCIONES
        =========================================== -->

        <div
          v-if="cargando"
          class="cycle-empty"
        >
          Cargando estructura escolar...
        </div>

        <section
          v-else
          class="cycle-section-grid"
        >
          <article
            v-for="seccion in secciones"
            :key="seccion.id_seccion"
            class="cycle-section-card"
          >
            <div class="cycle-section-top">
              <div>
                <p class="cycle-section-eyebrow">
                  GRADO Y SECCIÓN
                </p>

                <h3>
                  {{ seccion.etiqueta }}
                </h3>
              </div>

              <span class="cycle-section-count">
                {{ seccion.estudiantes }}
              </span>
            </div>

            <p class="cycle-section-label">
              Responsable principal
            </p>

            <strong class="cycle-section-teacher">
              {{ seccion.docente }}
            </strong>

            <div class="cycle-section-foot">
              <span
                class="cycle-badge"
                :class="
                  seccion.activo
                    ? 'cycle-badge-success'
                    : 'cycle-badge-neutral'
                "
              >
                {{
                  seccion.activo
                    ? "Activo"
                    : "Inactivo"
                }}
              </span>

              <button
                v-if="ciclo?.editable"
                type="button"
                class="cycle-btn cycle-btn-soft cycle-btn-sm"
                @click="abrirResponsable(seccion)"
              >
                Configurar
              </button>

              <span
                v-else
                class="cycle-muted"
              >
                Solo consulta
              </span>
            </div>
          </article>

          <div
            v-if="!secciones.length"
            class="cycle-empty"
          >
            Este ciclo todavía no tiene grados ni secciones.
          </div>
        </section>
      </main>
    </div>

    <!-- ==========================================
         MODAL AGREGAR SECCIÓN
    =========================================== -->

    <div
      v-if="modalSeccion"
      class="cycle-overlay"
      @click.self="cerrarAgregarSeccion"
    >
      <section class="cycle-modal cycle-modal-sm">
        <header class="cycle-modal-head">
          <div>
            <p>
              ESTRUCTURA ESCOLAR
            </p>

            <h2>
              Agregar grado y sección
            </h2>
          </div>

          <button
            type="button"
            class="cycle-close"
            @click="cerrarAgregarSeccion"
          >
            ×
          </button>
        </header>

        <div class="cycle-modal-body">
          <div class="cycle-form-two">
            <div class="cycle-form-group">
              <label class="required">
                Grado
              </label>

              <select
                v-model="formSeccion.grado"
                class="cycle-input"
              >
                <option value="1">
                  Primero
                </option>

                <option value="2">
                  Segundo
                </option>

                <option value="3">
                  Tercero
                </option>

                <option value="4">
                  Cuarto
                </option>

                <option value="5">
                  Quinto
                </option>

                <option value="6">
                  Sexto
                </option>
              </select>
            </div>

            <div class="cycle-form-group">
              <label class="required">
                Sección
              </label>

              <input
                v-model.trim="formSeccion.nombre"
                maxlength="2"
                class="cycle-input"
              />
            </div>
          </div>

          <div class="cycle-form-group">
            <label>
              Docente responsable
            </label>

            <select
              v-model="formSeccion.id_docente"
              class="cycle-input"
            >
              <option value="">
                Asignar después
              </option>

              <option
                v-for="docente in docentes"
                :key="docente.id_usuario"
                :value="docente.id_usuario"
              >
                {{ docente.nombre }}
              </option>
            </select>
          </div>

          <p class="cycle-hint">
            La sección tendrá un único responsable principal;
            el docente puede atender otras secciones.
          </p>

          <div
            v-if="errorModal"
            class="cycle-alert cycle-alert-error"
          >
            {{ errorModal }}
          </div>
        </div>

        <footer class="cycle-modal-footer">
          <button
            type="button"
            class="cycle-btn cycle-btn-secondary"
            @click="cerrarAgregarSeccion"
          >
            Cancelar
          </button>

          <button
            type="button"
            class="cycle-btn cycle-btn-primary"
            :disabled="procesando"
            @click="guardarSeccion"
          >
            {{
              procesando
                ? "Guardando..."
                : "Agregar sección"
            }}
          </button>
        </footer>
      </section>
    </div>

    <!-- ==========================================
         MODAL RESPONSABLE
    =========================================== -->

    <div
      v-if="modalResponsable"
      class="cycle-overlay"
      @click.self="cerrarResponsable"
    >
      <section class="cycle-modal cycle-modal-sm">
        <header class="cycle-modal-head">
          <div>
            <p>
              CONFIGURACIÓN DE SECCIÓN
            </p>

            <h2>
              {{ seccionConfig?.etiqueta }}
            </h2>
          </div>

          <button
            type="button"
            class="cycle-close"
            @click="cerrarResponsable"
          >
            ×
          </button>
        </header>

        <div class="cycle-modal-body">
          <div class="cycle-form-group">
            <label>
              Responsable actual
            </label>

            <div class="cycle-current-teacher">
              <span>
                ♟
              </span>

              <strong>
                {{ seccionConfig?.docente }}
              </strong>
            </div>
          </div>

          <div class="cycle-form-group">
            <label>
              Nuevo responsable
            </label>

            <select
              v-model="formResponsable.id_docente"
              class="cycle-input"
            >
              <option value="">
                Sin responsable
              </option>

              <option
                v-for="docente in docentes"
                :key="docente.id_usuario"
                :value="docente.id_usuario"
              >
                {{ docente.nombre }}
              </option>
            </select>
          </div>

          <p class="cycle-hint">
            Un docente puede atender varias secciones.
            Esta sección mantendrá un único responsable principal.
          </p>

          <div
            v-if="errorModal"
            class="cycle-alert cycle-alert-error"
          >
            {{ errorModal }}
          </div>
        </div>

        <footer class="cycle-modal-footer">
          <button
            type="button"
            class="cycle-btn cycle-btn-secondary"
            @click="cerrarResponsable"
          >
            Cancelar
          </button>

          <button
            type="button"
            class="cycle-btn cycle-btn-primary"
            :disabled="procesando"
            @click="guardarResponsable"
          >
            {{
              procesando
                ? "Guardando..."
                : "Guardar asignación"
            }}
          </button>
        </footer>
      </section>
    </div>

    <!-- ==========================================
         MODAL CREAR CICLO
    =========================================== -->

    <div
      v-if="modalCiclo"
      class="cycle-overlay"
      @click.self="cerrarCrearCiclo"
    >
      <section class="cycle-modal cycle-modal-lg">
        <header class="cycle-modal-head">
          <div>
            <p>
              NUEVO CICLO ESCOLAR
            </p>

            <h2>
              Preparar ciclo {{ formCiclo.anio }}
            </h2>
          </div>

          <button
            type="button"
            class="cycle-close"
            @click="cerrarCrearCiclo"
          >
            ×
          </button>
        </header>

        <div class="cycle-modal-body">
          <div class="cycle-stepper">
            <span class="done"></span>
            <span class="active"></span>
            <span></span>
            <span></span>
          </div>

          <div class="cycle-form-three">
            <div class="cycle-form-group">
              <label class="required">
                Año
              </label>

              <input
                v-model.number="formCiclo.anio"
                type="number"
                min="2026"
                max="2100"
                class="cycle-input"
              />
            </div>

            <div class="cycle-form-group">
              <label class="required">
                Fecha de inicio
              </label>

              <input
                v-model="formCiclo.fecha_inicio"
                type="date"
                class="cycle-input"
              />
            </div>

            <div class="cycle-form-group">
              <label class="required">
                Fecha de finalización
              </label>

              <input
                v-model="formCiclo.fecha_fin"
                type="date"
                class="cycle-input"
              />
            </div>
          </div>

          <div class="cycle-check-grid">
            <label class="cycle-check-card">
              <input
                v-model="formCiclo.copiar_estructura"
                type="checkbox"
              />

              <span>
                <strong>
                  Copiar grados y secciones
                </strong>

                <small>
                  Utilizar la estructura del ciclo activo.
                </small>
              </span>
            </label>

            <label class="cycle-check-card">
              <input
                v-model="formCiclo.conservar_responsables"
                type="checkbox"
                :disabled="!formCiclo.copiar_estructura"
              />

              <span>
                <strong>
                  Conservar responsables
                </strong>

                <small>
                  Asignar los mismos docentes.
                </small>
              </span>
            </label>

            <label class="cycle-check-card">
              <input
                v-model="formCiclo.promover_estudiantes"
                type="checkbox"
                :disabled="!formCiclo.copiar_estructura"
              />

              <span>
                <strong>
                  Promover estudiantes
                </strong>

                <small>
                  Crear matrículas en el grado siguiente.
                </small>
              </span>
            </label>
          </div>

          <div class="cycle-warning">
            <span>
              ⚠
            </span>

            <p>
              Revise los datos. El nuevo ciclo se creará
              como activo y el ciclo anterior se cerrará
              automáticamente, quedando disponible
              únicamente para consulta.
            </p>
          </div>

          <div
            v-if="errorModal"
            class="cycle-alert cycle-alert-error"
          >
            {{ errorModal }}
          </div>
        </div>

        <footer class="cycle-modal-footer">
          <button
            type="button"
            class="cycle-btn cycle-btn-secondary"
            @click="cerrarCrearCiclo"
          >
            Cancelar
          </button>

          <button
            type="button"
            class="cycle-btn cycle-btn-primary"
            :disabled="procesando"
            @click="guardarCiclo"
          >
            {{
              procesando
                ? "Creando..."
                : "Crear ciclo"
            }}
          </button>
        </footer>
      </section>
    </div>

    <!-- ==========================================
         CONFIRMAR CIERRE
    =========================================== -->

    <div
      v-if="modalCerrar"
      class="cycle-overlay cycle-overlay-front"
      @click.self="modalCerrar = false"
    >
      <section class="cycle-modal cycle-modal-sm">
        <header class="cycle-modal-head">
          <div>
            <p>
              CONFIRMACIÓN
            </p>

            <h2>
              Cerrar ciclo {{ ciclo?.anio }}
            </h2>
          </div>
        </header>

        <div class="cycle-modal-body">
          <p class="cycle-confirm-text">
            Las acciones de escritura quedarán bloqueadas.
            La información seguirá disponible para consulta.
          </p>

          <div class="cycle-warning">
            <span>
              ⚠
            </span>

            <p>
              Esta acción impedirá nuevas matrículas,
              documentos y cambios de estructura.
            </p>
          </div>
        </div>

        <footer class="cycle-modal-footer">
          <button
            type="button"
            class="cycle-btn cycle-btn-secondary"
            @click="modalCerrar = false"
          >
            Cancelar
          </button>

          <button
            type="button"
            class="cycle-btn cycle-btn-danger"
            :disabled="procesando"
            @click="confirmarCerrarCiclo"
          >
            {{
              procesando
                ? "Cerrando..."
                : "Cerrar ciclo"
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
  obtenerCiclos,
  obtenerCatalogosCiclo,
  crearSeccion,
  actualizarResponsable,
  cerrarCiclo,
  crearCiclo
} from "../../services/ciclosService";

import "../../assets/css/ciclo-escolar.css";

export default {
  name: "CicloEscolarView",

  components: {
    DirectorSidebar,
    DirectorTopbar
  },

  data() {
    return {
      ciclo: null,
      ciclos: [],
      secciones: [],
      docentes: [],

      cicloSeleccionadoId: "",

      cargando: true,
      procesando: false,

      mensaje: "",
      error: "",
      errorModal: "",

      modalSeccion: false,
      modalResponsable: false,
      modalCiclo: false,
      modalCerrar: false,

      seccionConfig: null,

      formSeccion: {
        grado: "1",
        nombre: "A",
        id_docente: ""
      },

      formResponsable: {
        id_docente: ""
      },

      formCiclo: {
        anio: 2027,
        fecha_inicio: "2027-01-05",
        fecha_fin: "2027-10-30",
        copiar_estructura: true,
        conservar_responsables: false,
        promover_estudiantes: false
      }
    };
  },

  async mounted() {
    const cicloGuardado =
      this.$route.query.id_ciclo ||
      localStorage.getItem(
        "sgad_ciclo"
      ) ||
      null;

    await Promise.all([
      this.cargarModulo(
        cicloGuardado
          ? Number(cicloGuardado)
          : null
      ),

      this.cargarCatalogos()
    ]);

    window.addEventListener(
      "sgad-cycle-changed",
      this.escucharCambioCiclo
    );
  },

  beforeUnmount() {
    window.removeEventListener(
      "sgad-cycle-changed",
      this.escucharCambioCiclo
    );
  },

  methods: {
    async cargarModulo(
      idCiclo = null
    ) {
      this.cargando = true;
      this.error = "";

      try {
        const data =
          await obtenerCiclos(
            idCiclo
          );

        this.ciclo =
          data.ciclo;

        this.ciclos =
          data.ciclos || [];

        this.secciones =
          data.secciones || [];

        this.cicloSeleccionadoId =
          String(
            this.ciclo?.id_ciclo ||
            ""
          );

        if (
          this.ciclo?.id_ciclo
        ) {
          localStorage.setItem(
            "sgad_ciclo",
            String(
              this.ciclo.id_ciclo
            )
          );
        }

      } catch (error) {
        console.error(error);

        this.error =
          error.response?.data?.mensaje ||
          "No fue posible cargar el ciclo escolar.";

      } finally {
        this.cargando = false;
      }
    },

    async cargarCatalogos() {
      try {
        const data =
          await obtenerCatalogosCiclo();

        this.docentes =
          data.docentes || [];

      } catch (error) {
        console.error(error);
      }
    },

    async escucharCambioCiclo(
      event
    ) {
      const idCiclo =
        event.detail?.id_ciclo;

      if (!idCiclo) {
        return;
      }

      if (
        String(idCiclo) ===
        String(
          this.ciclo?.id_ciclo
        )
      ) {
        return;
      }

      await this.cargarModulo(
        Number(idCiclo)
      );
    },

    async cambiarCiclo() {
      const idCiclo =
        Number(
          this.cicloSeleccionadoId
        );

      if (!idCiclo) {
        return;
      }

      localStorage.setItem(
        "sgad_ciclo",
        String(idCiclo)
      );

      await this.$router.replace({
        query: {
          ...this.$route.query,
          id_ciclo:
            String(idCiclo)
        }
      });

      await this.cargarModulo(
        idCiclo
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
    },

    abrirAgregarSeccion() {
      this.formSeccion = {
        grado: "1",
        nombre: "A",
        id_docente: ""
      };

      this.errorModal = "";
      this.modalSeccion = true;
    },

    cerrarAgregarSeccion() {
      if (this.procesando) {
        return;
      }

      this.modalSeccion = false;
      this.errorModal = "";
    },

    async guardarSeccion() {
      if (
        !this.formSeccion.nombre.trim()
      ) {
        this.errorModal =
          "Ingrese la sección.";

        return;
      }

      this.procesando = true;
      this.errorModal = "";

      try {
        const respuesta =
          await crearSeccion({
            id_ciclo:
              this.ciclo.id_ciclo,

            grado:
              Number(
                this.formSeccion.grado
              ),

            nombre:
              this.formSeccion.nombre
                .trim()
                .toUpperCase(),

            id_docente:
              this.formSeccion.id_docente
                ? Number(
                    this.formSeccion.id_docente
                  )
                : null
          });

        this.mensaje =
          respuesta.mensaje;

        this.modalSeccion =
          false;

        await this.cargarModulo(
          this.ciclo.id_ciclo
        );

      } catch (error) {
        console.error(error);

        this.errorModal =
          error.response?.data?.mensaje ||
          "No fue posible agregar la sección.";

      } finally {
        this.procesando = false;
      }
    },

    abrirResponsable(
      seccion
    ) {
      this.seccionConfig =
        seccion;

      this.formResponsable = {
        id_docente:
          seccion.id_docente ||
          ""
      };

      this.errorModal = "";
      this.modalResponsable =
        true;
    },

    cerrarResponsable() {
      if (this.procesando) {
        return;
      }

      this.modalResponsable =
        false;

      this.seccionConfig =
        null;

      this.errorModal = "";
    },

    async guardarResponsable() {
      this.procesando = true;
      this.errorModal = "";

      try {
        const respuesta =
          await actualizarResponsable(
            this.seccionConfig.id_seccion,

            this.formResponsable.id_docente
              ? Number(
                  this.formResponsable.id_docente
                )
              : null
          );

        this.mensaje =
          respuesta.mensaje;

        this.modalResponsable =
          false;

        this.seccionConfig =
          null;

        await this.cargarModulo(
          this.ciclo.id_ciclo
        );

      } catch (error) {
        console.error(error);

        this.errorModal =
          error.response?.data?.mensaje ||
          "No fue posible actualizar el responsable.";

      } finally {
        this.procesando =
          false;
      }
    },

    abrirCrearCiclo() {
      const maxYear =
        this.ciclos.length
          ? Math.max(
              ...this.ciclos.map(
                item =>
                  item.anio
              )
            )
          : new Date()
              .getFullYear();

      const siguiente =
        maxYear + 1;

      this.formCiclo = {
        anio:
          siguiente,

        fecha_inicio:
          `${siguiente}-01-05`,

        fecha_fin:
          `${siguiente}-10-30`,

        copiar_estructura:
          true,

        conservar_responsables:
          false,

        promover_estudiantes:
          false
      };

      this.errorModal = "";
      this.modalCiclo = true;
    },

    cerrarCrearCiclo() {
      if (this.procesando) {
        return;
      }

      this.modalCiclo =
        false;

      this.errorModal =
        "";
    },

    async guardarCiclo() {
      if (
        !this.formCiclo.anio ||
        !this.formCiclo.fecha_inicio ||
        !this.formCiclo.fecha_fin
      ) {
        this.errorModal =
          "Complete los datos obligatorios.";

        return;
      }

      if (
        this.formCiclo.fecha_fin <=
        this.formCiclo.fecha_inicio
      ) {
        this.errorModal =
          "La fecha final debe ser posterior a la inicial.";

        return;
      }

      if (
        this.formCiclo.promover_estudiantes &&
        !this.formCiclo.copiar_estructura
      ) {
        this.errorModal =
          "Para promover estudiantes debe copiar la estructura.";

        return;
      }

      this.procesando =
        true;

      this.errorModal =
        "";

      try {
        const respuesta =
          await crearCiclo(
            this.formCiclo
          );

        this.mensaje =
          respuesta.mensaje;

        this.modalCiclo =
          false;

        const nuevoId =
          Number(
            respuesta.id_ciclo
          );

        localStorage.setItem(
          "sgad_ciclo",
          String(nuevoId)
        );

        await this.$router.replace({
          query: {
            ...this.$route.query,
            id_ciclo:
              String(nuevoId)
          }
        });

        await this.cargarModulo(
          nuevoId
        );

        window.dispatchEvent(
          new CustomEvent(
            "sgad-cycle-changed",
            {
              detail: {
                id_ciclo:
                  nuevoId
              }
            }
          )
        );

      } catch (error) {
        console.error(error);

        this.errorModal =
          error.response?.data?.mensaje ||
          "No fue posible crear el ciclo escolar.";

      } finally {
        this.procesando =
          false;
      }
    },

    abrirCerrarCiclo() {
      this.modalCerrar =
        true;
    },

    async confirmarCerrarCiclo() {
      this.procesando =
        true;

      this.error =
        "";

      try {
        const respuesta =
          await cerrarCiclo(
            this.ciclo.id_ciclo
          );

        this.mensaje =
          respuesta.mensaje;

        this.modalCerrar =
          false;

        await this.cargarModulo(
          this.ciclo.id_ciclo
        );

        window.dispatchEvent(
          new CustomEvent(
            "sgad-cycle-changed",
            {
              detail: {
                id_ciclo:
                  this.ciclo.id_ciclo
              }
            }
          )
        );

      } catch (error) {
        console.error(error);

        this.error =
          error.response?.data?.mensaje ||
          "No fue posible cerrar el ciclo.";

      } finally {
        this.procesando =
          false;
      }
    },

    formatearFecha(fecha) {
      if (!fecha) {
        return "—";
      }

      return new Intl.DateTimeFormat(
        "es-GT",
        {
          day: "numeric",
          month: "short",
          year: "numeric"
        }
      ).format(
        new Date(
          `${fecha}T12:00:00`
        )
      );
    }
  }
};
</script>