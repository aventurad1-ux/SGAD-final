<template>
  <div class="teacher-layout">
    <TeacherSidebar />

    <div class="teacher-main">
      <TeacherTopbar
        :notificaciones="notificaciones"
        :items-notificaciones="itemsNotificaciones"
        :ciclos="ciclos"
        :ciclo-seleccionado="ciclo"
        @cambiar-ciclo="cambiarCiclo"
        @abrir-notificacion="abrirNotificacion"
      />

      <main class="teacher-content">
        <!-- ==========================================
             HERO
        =========================================== -->

        <section class="teacher-hero">
          <div class="teacher-hero-decoration"></div>

          <div class="teacher-hero-content">
            <p>
              PANEL DOCENTE · CICLO {{ ciclo?.anio || "—" }}
            </p>

            <h1>
              Hola, {{ primerNombre }}
            </h1>

            <span>
              Secciones asignadas:
              <strong>
                {{ etiquetasSecciones }}.
              </strong>
            </span>
          </div>

          <button
            type="button"
            class="teacher-hero-button"
            @click="irEntregas"
          >
            Ver entregas
          </button>
        </section>

        <div
          v-if="error"
          class="teacher-alert-error"
        >
          {{ error }}
        </div>

        <!-- ==========================================
             INDICADORES
        =========================================== -->

        <section class="teacher-kpi-grid">
          <!-- ESTUDIANTES -->

          <article class="teacher-kpi-card teacher-kpi-green">
            <div class="teacher-kpi-body">
              <div class="teacher-kpi-head">
                <span>
                  MIS ESTUDIANTES
                </span>

                <div class="teacher-kpi-icon">
                  ◎
                </div>
              </div>

              <strong class="teacher-kpi-number">
                {{ totalEstudiantes }}
              </strong>

              <p>
                Asignados a mis secciones
              </p>
            </div>

            <div class="teacher-kpi-footer">
              <span>
                Información actualizada
              </span>

              <button
                type="button"
                @click="irEstudiantes"
              >
                Ver →
              </button>
            </div>
          </article>

          <!-- SOLICITUDES -->

          <article class="teacher-kpi-card teacher-kpi-yellow">
            <div class="teacher-kpi-body">
              <div class="teacher-kpi-head">
                <span>
                  SOLICITUDES
                  <br />
                  PENDIENTES
                </span>

                <div class="teacher-kpi-icon">
                  ◷
                </div>
              </div>

              <strong class="teacher-kpi-number">
                {{ solicitudesPendientes }}
              </strong>

              <p>
                Requieren una entrega
              </p>
            </div>

            <div class="teacher-kpi-footer">
              <span>
                Información actualizada
              </span>

              <button
                type="button"
                @click="irEntregas"
              >
                Ver →
              </button>
            </div>
          </article>

          <!-- APROBADOS -->

          <article class="teacher-kpi-card teacher-kpi-blue">
            <div class="teacher-kpi-body">
              <div class="teacher-kpi-head">
                <span>
                  DOCUMENTOS
                  <br />
                  APROBADOS
                </span>

                <div class="teacher-kpi-icon">
                  ✓
                </div>
              </div>

              <strong class="teacher-kpi-number">
                {{ documentosAprobados }}
              </strong>

              <p>
                Revisados por Dirección
              </p>
            </div>

            <div class="teacher-kpi-footer">
              <span>
                Información actualizada
              </span>

              <button
                type="button"
                @click="irDocumentos"
              >
                Ver →
              </button>
            </div>
          </article>

          <!-- CORRECCIONES -->

          <article class="teacher-kpi-card teacher-kpi-red">
            <div class="teacher-kpi-body">
              <div class="teacher-kpi-head">
                <span>
                  CORRECCIONES
                </span>

                <div class="teacher-kpi-icon">
                  ↻
                </div>
              </div>

              <strong class="teacher-kpi-number">
                {{ correcciones }}
              </strong>

              <p>
                Necesitan una nueva versión
              </p>
            </div>

            <div class="teacher-kpi-footer">
              <span>
                Información actualizada
              </span>

              <button
                type="button"
                @click="irCorrecciones"
              >
                Ver →
              </button>
            </div>
          </article>
        </section>

        <!-- ==========================================
             PANELES INFERIORES
        =========================================== -->

        <section class="teacher-bottom-grid">
          <!-- PRÓXIMAS ENTREGAS -->

          <article class="teacher-bottom-card">
            <header>
              <div>
                <h2>
                  Próximas entregas
                </h2>

                <p>
                  Solicitudes activas que requieren atención
                </p>
              </div>
            </header>

            <div
              v-if="cargando"
              class="teacher-empty-deliveries"
            >
              Cargando entregas...
            </div>

            <div
              v-else-if="proximasEntregas.length"
              class="teacher-delivery-list"
            >
              <article
                v-for="entrega in proximasEntregas"
                :key="entrega.id_destinatario"
                class="teacher-delivery-row"
              >
                <div class="teacher-delivery-icon">
                  {{
                    entrega.estado === "correccion_solicitada"
                      ? "↻"
                      : "◷"
                  }}
                </div>

                <div class="teacher-delivery-text">
                  <strong>
                    {{ entrega.titulo }}
                  </strong>

                  <span>
                    {{ detalleEntrega(entrega) }}
                  </span>
                </div>

                <button
                  type="button"
                  @click="abrirEntrega(entrega)"
                >
                  Abrir
                </button>
              </article>
            </div>

            <div
              v-else
              class="teacher-empty-deliveries"
            >
              <div>
                ◷
              </div>

              <strong>
                Sin entregas pendientes
              </strong>

              <span>
                No hay solicitudes activas por atender.
              </span>
            </div>
          </article>

          <!-- MIS SECCIONES -->

          <article class="teacher-bottom-card">
            <header>
              <div>
                <h2>
                  Mis secciones
                </h2>

                <p>
                  Responsabilidades del ciclo seleccionado
                </p>
              </div>
            </header>

            <div
              v-if="cargando"
              class="teacher-empty-deliveries"
            >
              Cargando secciones...
            </div>

            <div
              v-else-if="!misSecciones.length"
              class="teacher-empty-deliveries"
            >
              <strong>
                Sin secciones asignadas
              </strong>

              <span>
                Dirección aún no le ha asignado secciones.
              </span>
            </div>

            <div
              v-else
              class="teacher-sections-box"
            >
              <article
                v-for="seccion in misSecciones"
                :key="seccion.id_seccion"
                class="teacher-section-row"
              >
                <div class="teacher-section-left">
                  <div class="teacher-section-icon">
                    ▱
                  </div>

                  <div>
                    <strong>
                      {{ seccion.etiqueta }}
                    </strong>

                    <span>
                      {{ seccion.estudiantes }}
                      {{
                        seccion.estudiantes === 1
                          ? "estudiante asignado"
                          : "estudiantes asignados"
                      }}
                    </span>
                  </div>
                </div>

                <span class="teacher-section-status">
                  Activa
                </span>
              </article>
            </div>
          </article>
        </section>
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
  obtenerCiclos
} from "../../services/ciclosService";

import {
  obtenerSolicitudesDocente
} from "../../services/docenteSolicitudesService";

import {
  obtenerDocumentosDocente
} from "../../services/docenteDocumentosService";

import "../../assets/css/teacher.css";


export default {
  name: "TeacherDashboardView",

  components: {
    TeacherSidebar,
    TeacherTopbar
  },


  data() {
    return {
      ciclo: null,
      ciclos: [],

      misSecciones: [],
      solicitudes: [],
      documentos: [],

      usuario: null,

      cargando: true,
      error: ""
    };
  },


  computed: {
    primerNombre() {
      return (
        this.usuario?.nombres
          ?.split(" ")[0]
        || "Docente"
      );
    },


    totalEstudiantes() {
      return this.misSecciones.reduce(
        (total, seccion) =>
          total +
          Number(
            seccion.estudiantes || 0
          ),
        0
      );
    },


    etiquetasSecciones() {
      if (!this.misSecciones.length) {
        return "Sin asignación";
      }

      return this.misSecciones
        .map(
          seccion =>
            seccion.etiqueta
        )
        .join(" y ");
    },


    solicitudesPendientes() {
      return this.solicitudes.filter(
        solicitud =>
          solicitud.estado === "pendiente"
          || solicitud.estado === "vencido"
      ).length;
    },


    documentosAprobados() {
      return this.documentos.filter(
        documento =>
          documento.estado === "aprobado"
      ).length;
    },


    correcciones() {
      return this.solicitudes.filter(
        solicitud =>
          solicitud.estado
          === "correccion_solicitada"
      ).length;
    },


    proximasEntregas() {
      const solicitudes =
        this.solicitudes.filter(
          solicitud =>
            solicitud.estado === "pendiente"
            || solicitud.estado === "vencido"
            || solicitud.estado
              === "correccion_solicitada"
        );

      return solicitudes
        .sort(
          (a, b) => {
            const fechaA =
              a.fecha_limite
                ? new Date(
                    a.fecha_limite
                  ).getTime()
                : Number.MAX_SAFE_INTEGER;

            const fechaB =
              b.fecha_limite
                ? new Date(
                    b.fecha_limite
                  ).getTime()
                : Number.MAX_SAFE_INTEGER;

            return fechaA - fechaB;
          }
        )
        .slice(0, 5);
    },


    notificaciones() {
      return this.itemsNotificaciones.length;
    },


    itemsNotificaciones() {
      return this.solicitudes
        .filter(
          solicitud =>
            solicitud.estado === "pendiente"
            || solicitud.estado === "vencido"
            || solicitud.estado
              === "correccion_solicitada"
        )
        .map(
          solicitud => {
            const esCorreccion =
              solicitud.estado
              === "correccion_solicitada";

            return {
              id:
                solicitud.id_destinatario,

              id_destinatario:
                solicitud.id_destinatario,

              titulo:
                solicitud.titulo,

              estado:
                solicitud.estado,

              tipo:
                esCorreccion
                  ? "correccion"
                  : "solicitud",

              mensaje:
                esCorreccion
                  ? `Dirección solicitó correcciones en: ${solicitud.titulo}`
                  : `Dirección solicitó: ${solicitud.titulo}`,

              fecha_limite:
                solicitud.fecha_limite
            };
          }
        );
    }
  },


  async mounted() {
    this.cargarUsuario();

    await this.cargarDashboard();
  },


  methods: {
    cargarUsuario() {
      try {
        this.usuario =
          JSON.parse(
            localStorage.getItem(
              "usuario"
            ) || "{}"
          );

      } catch {
        this.usuario = null;
      }
    },


    async cargarDashboard() {
      this.cargando = true;
      this.error = "";

      try {
        /*
         * Primero consultamos todos los ciclos.
         */
        const data =
          await obtenerCiclos();

        this.ciclos =
          data.ciclos || [];


        /*
         * Si anteriormente el usuario seleccionó
         * un ciclo, intentamos conservarlo.
         */
        const cicloGuardado =
          Number(
            localStorage.getItem(
              "sgad_ciclo"
            )
          );


        let cicloSeleccionado =
          null;


        if (
          cicloGuardado
          && !Number.isNaN(
            cicloGuardado
          )
        ) {
          cicloSeleccionado =
            this.ciclos.find(
              item =>
                Number(
                  item.id_ciclo
                ) === cicloGuardado
            );
        }


        /*
         * Si no había ciclo guardado,
         * utilizamos el ciclo activo.
         */
        if (!cicloSeleccionado) {
          cicloSeleccionado =
            this.ciclos.find(
              item =>
                item.estado === "activo"
            )
            || data.ciclo
            || null;
        }


        this.ciclo =
          cicloSeleccionado;


        if (!this.ciclo) {
          this.misSecciones = [];
          this.solicitudes = [];
          this.documentos = [];

          return;
        }


        await this.cargarDatosCiclo(
          this.ciclo.id_ciclo
        );

      } catch (error) {
        console.error(
          "ERROR PANEL DOCENTE:",
          error
        );

        this.error =
          error.response?.data?.mensaje
          || error.response?.data?.message
          || "No fue posible cargar el panel docente.";

      } finally {
        this.cargando = false;
      }
    },


    async cargarDatosCiclo(
      idCiclo
    ) {
      if (!idCiclo) {
        return;
      }


      const [
        cicloData,
        solicitudesData,
        documentosData
      ] =
        await Promise.all([
          obtenerCiclos(
            idCiclo
          ),

          obtenerSolicitudesDocente(
            idCiclo
          ),

          obtenerDocumentosDocente()
        ]);


      /*
       * SECCIONES DEL DOCENTE
       */
      const idUsuario =
        Number(
          this.usuario?.id_usuario
        );


      this.misSecciones =
        (
          cicloData.secciones || []
        ).filter(
          seccion =>
            Number(
              seccion.id_docente
            ) === idUsuario
        );


      /*
       * SOLICITUDES DEL CICLO
       */
      this.solicitudes =
        solicitudesData.solicitudes || [];


      /*
       * DOCUMENTOS DEL CICLO
       *
       * El endpoint de documentos devuelve
       * documentos de todos los ciclos del docente,
       * por eso filtramos usando id_ciclo.
       */
      this.documentos =
        (
          documentosData.documentos || []
        ).filter(
          documento =>
            Number(
              documento.id_ciclo
            ) === Number(
              idCiclo
            )
        );


      localStorage.setItem(
        "sgad_ciclo",
        String(
          idCiclo
        )
      );


      /*
       * Avisamos al Sidebar para que vuelva
       * a calcular sus contadores.
       */
      window.dispatchEvent(
        new Event(
          "sgad-actualizar-contadores-docente"
        )
      );
    },


    async cambiarCiclo(
      valor
    ) {
      let idCiclo =
        valor;


      /*
       * Permitimos que TeacherTopbar envíe
       * directamente el id o el objeto ciclo.
       */
      if (
        typeof valor === "object"
        && valor !== null
      ) {
        idCiclo =
          valor.id_ciclo;
      }


      idCiclo =
        Number(
          idCiclo
        );


      if (
        !idCiclo
        || Number.isNaN(
          idCiclo
        )
      ) {
        return;
      }


      const nuevoCiclo =
        this.ciclos.find(
          item =>
            Number(
              item.id_ciclo
            ) === idCiclo
        );


      if (!nuevoCiclo) {
        return;
      }


      this.ciclo =
        nuevoCiclo;


      this.cargando =
        true;

      this.error =
        "";


      try {
        await this.cargarDatosCiclo(
          nuevoCiclo.id_ciclo
        );

      } catch (error) {
        console.error(
          "ERROR CAMBIO CICLO:",
          error
        );

        this.error =
          error.response?.data?.mensaje
          || "No fue posible cambiar el ciclo escolar.";

      } finally {
        this.cargando =
          false;
      }
    },


    detalleEntrega(
      entrega
    ) {
      const partes = [];


      if (entrega.fecha_limite) {
        partes.push(
          `Vence ${this.formatearFecha(
            entrega.fecha_limite
          )}`
        );
      }


      const formatos =
        entrega.formatos_permitidos
        || [];


      if (formatos.length) {
        partes.push(
          formatos.join(", ")
        );
      }


      if (
        entrega.estado
        === "correccion_solicitada"
      ) {
        partes.push(
          "Corrección solicitada"
        );
      }


      return partes.join(" · ");
    },


    formatearFecha(
      valor
    ) {
      if (!valor) {
        return "—";
      }


      const fecha =
        new Date(
          `${valor}T00:00:00`
        );


      return fecha.toLocaleDateString(
        "es-GT",
        {
          day: "2-digit",
          month: "short",
          year: "numeric"
        }
      );
    },


    irEstudiantes() {
      this.$router.push(
        "/docente/estudiantes"
      );
    },


    irEntregas() {
      this.$router.push(
        "/docente/solicitudes"
      );
    },


    irDocumentos() {
      this.$router.push(
        "/docente/documentos"
      );
    },


    irCorrecciones() {
      this.$router.push(
        "/docente/correcciones"
      );
    },


    abrirEntrega(
      entrega
    ) {
      if (!entrega) {
        return;
      }


      if (
        entrega.estado
        === "correccion_solicitada"
      ) {
        this.$router.push({
          path:
            "/docente/correcciones",

          query: {
            abrir:
              entrega.id_destinatario
          }
        });

        return;
      }


      this.$router.push({
        path:
          "/docente/solicitudes",

        query: {
          abrir:
            entrega.id_destinatario
        }
      });
    },


    abrirNotificacion(
      notificacion
    ) {
      if (!notificacion) {
        return;
      }


      if (
        notificacion.tipo
        === "correccion"
      ) {
        this.$router.push({
          path:
            "/docente/correcciones",

          query: {
            abrir:
              notificacion.id_destinatario
          }
        });

        return;
      }


      this.$router.push({
        path:
          "/docente/solicitudes",

        query: {
          abrir:
            notificacion.id_destinatario
        }
      });
    }
  }
};
</script>