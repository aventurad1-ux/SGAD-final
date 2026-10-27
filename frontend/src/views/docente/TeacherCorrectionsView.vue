<template>
  <div class="teacher-page">
    <TeacherSidebar />

    <main class="teacher-main">
      <TeacherTopbar />

      <section class="corrections-page">
        <header class="corrections-header">
          <p class="corrections-kicker">
            ESPACIO DOCENTE
          </p>

          <h1>Correcciones</h1>

          <p class="corrections-subtitle">
            Revise las observaciones de Dirección y envíe una nueva versión
            cuando la solicitud esté vigente.
          </p>
        </header>

        <div
          v-if="error"
          class="corrections-empty"
        >
          {{ error }}
        </div>

        <div
          v-else-if="cargando"
          class="corrections-empty"
        >
          Cargando correcciones...
        </div>

        <div
          v-else-if="!correcciones.length"
          class="corrections-empty"
        >
          No tienes correcciones pendientes.
        </div>

        <div
          v-else
          class="corrections-grid"
        >
          <article
            v-for="correccion in correcciones"
            :key="correccion.id_destinatario"
            class="correction-card"
          >
            <div class="correction-card-top">
              <div>
                <h2>
                  {{ correccion.titulo }}
                </h2>

                <p>
                  {{ codigoEntrega(correccion) }}
                </p>
              </div>

              <span class="correction-badge">
                Corrección solicitada
              </span>
            </div>

            <div class="correction-observation">
              <span>⚠</span>

              <p>
                {{
                  correccion.observacion
                  || "Dirección solicitó una corrección."
                }}
              </p>
            </div>

            <button
              type="button"
              class="correction-send-button"
              @click="abrirCorreccion(correccion)"
            >
              Enviar nueva versión
            </button>
          </article>
        </div>
      </section>
    </main>

    <!-- =====================================================
         MODAL CORRECCIÓN
    ====================================================== -->

    <div
      v-if="mostrarModal"
      class="correction-overlay"
      @click.self="cerrarModal"
    >
      <section class="correction-modal">
        <header class="correction-modal-header">
          <div>
            <p>
              SOLICITUD DE DIRECCIÓN
            </p>

            <h2>
              {{ detalle?.titulo }}
            </h2>
          </div>

          <button
            type="button"
            class="correction-modal-x"
            @click="cerrarModal"
          >
            ×
          </button>
        </header>

        <div
          v-if="cargandoDetalle"
          class="correction-modal-loading"
        >
          Cargando solicitud...
        </div>

        <div
          v-else-if="detalle"
          class="correction-modal-body"
        >
          <div class="correction-info-grid">
            <div class="correction-info-item">
              <span>
                FECHA LÍMITE
              </span>

              <strong>
                {{ formatearFecha(detalle.fecha_limite) }}
              </strong>
            </div>

            <div class="correction-info-item">
              <span>
                PRIORIDAD
              </span>

              <strong>
                {{ textoPrioridad(detalle.prioridad) }}
              </strong>
            </div>

            <div class="correction-info-item">
              <span>
                FORMATOS PERMITIDOS
              </span>

              <strong>
                {{
                  detalle.formatos_permitidos?.length
                    ? detalle.formatos_permitidos.join(", ")
                    : "Sin especificar"
                }}
              </strong>
            </div>

            <div class="correction-info-item">
              <span>
                ESTADO
              </span>

              <strong>
                Corrección solicitada
              </strong>
            </div>
          </div>

          <p class="correction-description">
            {{ detalle.descripcion }}
          </p>

          <!-- OBSERVACIÓN DE DIRECCIÓN -->

          <div class="correction-director-note">
            <span>⚠</span>

            <p>
              <strong>Observaciones:</strong>
              {{
                observacionCorreccion
                || "Dirección solicitó realizar una corrección."
              }}
            </p>
          </div>

          <!-- ARCHIVO ACTUAL -->

          <div
            v-if="ultimaVersion"
            class="correction-file-box"
          >
            <span class="correction-file-icon">
              ▤
            </span>

            <span>
              Archivo entregado:
            </span>

            <strong>
              {{ ultimaVersion.nombre_archivo }}
            </strong>

            <span>
              · v{{ ultimaVersion.numero_version }}
            </span>
          </div>

          <!-- VERSIONES ANTERIORES -->

          <div
            v-if="versionesAnteriores.length"
            class="correction-versions"
          >
            <p>
              Versiones anteriores
            </p>

            <div
              v-for="version in versionesAnteriores"
              :key="version.id_version_entrega"
              class="correction-version-row"
            >
              <span>
                v{{ version.numero_version }}
              </span>

              <strong>
                {{ version.nombre_archivo }}
              </strong>
            </div>
          </div>

          <p
            v-else
            class="correction-no-versions"
          >
            No hay versiones anteriores.
          </p>

          <!-- NUEVA VERSIÓN -->

          <div class="correction-upload">
            <label>
              Seleccione el archivo
              <span>*</span>
            </label>

            <input
              type="file"
              :accept="acceptArchivo"
              @change="seleccionarArchivo"
            />

            <label>
              Observaciones
            </label>

            <textarea
              v-model="observaciones"
              rows="4"
            ></textarea>
          </div>
        </div>

        <footer class="correction-modal-footer">
          <button
            type="button"
            class="correction-modal-btn light"
            @click="cerrarModal"
          >
            Cerrar
          </button>

          <button
            v-if="ultimaVersion"
            type="button"
            class="correction-modal-btn view"
            @click="verArchivoActual"
          >
            Ver archivo
          </button>

          <button
            v-if="ultimaVersion"
            type="button"
            class="correction-modal-btn light"
            @click="descargarArchivoActual"
          >
            Descargar
          </button>

          <button
            type="button"
            class="correction-modal-btn primary"
            :disabled="enviando"
            @click="enviarCorreccion"
          >
            {{
              enviando
                ? "Enviando..."
                : "Enviar corrección"
            }}
          </button>
        </footer>
      </section>
    </div>
  </div>
</template>

<script setup>
import {
  computed,
  onMounted,
  ref,
} from "vue";

import {
  useRoute,
  useRouter,
} from "vue-router";

import TeacherSidebar from "../../components/layout/TeacherSidebar.vue";
import TeacherTopbar from "../../components/layout/TeacherTopbar.vue";

import {
  descargarArchivoEntrega,
  obtenerSolicitudDocente,
  obtenerSolicitudesDocente,
  realizarEntregaDocente,
  verArchivoEntrega,
} from "../../services/docenteSolicitudesService";

import "../../assets/css/teacher-corrections.css";


const route = useRoute();
const router = useRouter();


const correcciones = ref([]);

const cargando = ref(true);
const error = ref("");

const mostrarModal = ref(false);
const cargandoDetalle = ref(false);

const detalle = ref(null);

const archivoSeleccionado = ref(null);
const observaciones = ref("");

const enviando = ref(false);


const requisitoActual = computed(() => {
  return detalle.value?.requisitos?.[0] || null;
});


const ultimaVersion = computed(() => {
  return requisitoActual.value?.ultima_version || null;
});


const versionesAnteriores = computed(() => {
  const versiones =
    requisitoActual.value?.versiones || [];

  if (
    !versiones.length
    || !ultimaVersion.value
  ) {
    return [];
  }

  return versiones.filter(
    (version) =>
      version.id_version_entrega
      !== ultimaVersion.value.id_version_entrega
  );
});


const observacionCorreccion = computed(() => {
  return obtenerObservacionCorreccion(
    detalle.value
  );
});


const acceptArchivo = computed(() => {
  const formatos =
    requisitoActual.value?.formatos_permitidos
    || detalle.value?.formatos_permitidos
    || [];

  const lista = [];

  if (formatos.includes("PDF")) {
    lista.push(".pdf");
  }

  if (formatos.includes("DOCX")) {
    lista.push(".docx");
  }

  if (formatos.includes("XLSX")) {
    lista.push(".xlsx");
  }

  if (
    formatos.includes("PNG")
    || formatos.includes("PNG/JPG")
  ) {
    lista.push(
      ".png",
      ".jpg",
      ".jpeg"
    );
  }

  return lista.join(",");
});


function obtenerIdCiclo() {
  const valor =
    localStorage.getItem("sgad_ciclo");

  if (!valor) {
    return null;
  }

  const numero =
    Number(valor);

  return Number.isNaN(numero)
    ? null
    : numero;
}


async function cargarCorrecciones() {
  cargando.value = true;
  error.value = "";

  try {
    const data =
      await obtenerSolicitudesDocente(
        obtenerIdCiclo()
      );

    const pendientes =
      (data.solicitudes || []).filter(
        (solicitud) =>
          solicitud.estado
          === "correccion_solicitada"
      );

    const resultado =
      await Promise.all(
        pendientes.map(
          async (solicitud) => {
            try {
              const response =
                await obtenerSolicitudDocente(
                  solicitud.id_destinatario
                );

              const detalleSolicitud =
                response.solicitud;

              return {
                ...solicitud,

                observacion:
                  obtenerObservacionCorreccion(
                    detalleSolicitud
                  ),
              };

            } catch {
              return {
                ...solicitud,
                observacion: "",
              };
            }
          }
        )
      );

    correcciones.value =
      resultado;

    await abrirDesdeQuery();

  } catch (err) {
    error.value =
      err.response?.data?.mensaje
      || "No fue posible cargar las correcciones.";

  } finally {
    cargando.value = false;
  }
}


async function abrirDesdeQuery() {
  const idAbrir =
    Number(
      route.query.abrir
    );

  if (
    !idAbrir
    || Number.isNaN(
      idAbrir
    )
  ) {
    return;
  }

  const correccion =
    correcciones.value.find(
      item =>
        Number(
          item.id_destinatario
        ) === idAbrir
    );

  if (!correccion) {
    return;
  }

  await abrirCorreccion(
    correccion
  );

  /*
   * Quitamos ?abrir=... una vez que
   * el modal ya fue abierto.
   */
  await router.replace({
    path:
      "/docente/correcciones"
  });
}


async function abrirCorreccion(
  correccion
) {
  mostrarModal.value = true;
  cargandoDetalle.value = true;

  detalle.value = null;
  archivoSeleccionado.value = null;
  observaciones.value = "";

  try {
    const data =
      await obtenerSolicitudDocente(
        correccion.id_destinatario
      );

    detalle.value =
      data.solicitud;

  } catch (err) {
    window.alert(
      err.response?.data?.mensaje
      || "No fue posible abrir la corrección."
    );

    mostrarModal.value = false;

  } finally {
    cargandoDetalle.value = false;
  }
}


function obtenerObservacionCorreccion(
  solicitud
) {
  if (!solicitud) {
    return "";
  }

  const requisitos =
    solicitud.requisitos || [];

  const revisiones = [];

  requisitos.forEach(
    (requisito) => {
      const versiones = [
        ...(requisito.versiones || []),
      ];

      if (
        requisito.ultima_version
        && !versiones.some(
          (version) =>
            version.id_version_entrega
            === requisito.ultima_version.id_version_entrega
        )
      ) {
        versiones.push(
          requisito.ultima_version
        );
      }

      versiones.forEach(
        (version) => {
          (version.revisiones || [])
            .forEach(
              (revision) => {
                if (
                  revision.resultado
                  === "correccion_solicitada"
                ) {
                  revisiones.push(
                    revision
                  );
                }
              }
            );
        }
      );
    }
  );

  if (
    Array.isArray(
      solicitud.revisiones
    )
  ) {
    solicitud.revisiones
      .forEach(
        (revision) => {
          if (
            revision.resultado
            === "correccion_solicitada"
          ) {
            revisiones.push(
              revision
            );
          }
        }
      );
  }

  revisiones.sort(
    (a, b) => {
      const fechaA =
        new Date(
          a.fecha_revision || 0
        ).getTime();

      const fechaB =
        new Date(
          b.fecha_revision || 0
        ).getTime();

      return fechaB - fechaA;
    }
  );

  return (
    revisiones[0]?.observaciones
    || ""
  );
}


function seleccionarArchivo(event) {
  archivoSeleccionado.value =
    event.target.files?.[0]
    || null;
}


async function enviarCorreccion() {
  if (
    !detalle.value
    || !requisitoActual.value
  ) {
    return;
  }

  if (
    !archivoSeleccionado.value
  ) {
    window.alert(
      "Seleccione el archivo corregido."
    );

    return;
  }

  enviando.value = true;

  try {
    await realizarEntregaDocente(
      detalle.value.id_destinatario,
      requisitoActual.value.id_requisito_solicitud,
      archivoSeleccionado.value,
      observaciones.value
    );

    window.alert(
      "Corrección enviada correctamente."
    );

    cerrarModal();

    await cargarCorrecciones();

    /*
     * Actualizar inmediatamente los números
     * del Sidebar.
     */
    window.dispatchEvent(
      new Event(
        "sgad-actualizar-contadores-docente"
      )
    );

  } catch (err) {
    window.alert(
      err.response?.data?.mensaje
      || "No fue posible enviar la corrección."
    );

  } finally {
    enviando.value = false;
  }
}


async function verArchivoActual() {
  if (!ultimaVersion.value) {
    return;
  }

  try {
    const response =
      await verArchivoEntrega(
        ultimaVersion.value.id_version_entrega
      );

    const url =
      URL.createObjectURL(
        response.data
      );

    window.open(
      url,
      "_blank"
    );

    setTimeout(() => {
      URL.revokeObjectURL(
        url
      );
    }, 60000);

  } catch {
    window.alert(
      "No fue posible abrir el archivo."
    );
  }
}


async function descargarArchivoActual() {
  if (!ultimaVersion.value) {
    return;
  }

  try {
    const response =
      await descargarArchivoEntrega(
        ultimaVersion.value.id_version_entrega
      );

    const url =
      URL.createObjectURL(
        response.data
      );

    const link =
      document.createElement("a");

    link.href = url;

    link.download =
      ultimaVersion.value.nombre_archivo
      || "archivo";

    document.body.appendChild(
      link
    );

    link.click();
    link.remove();

    URL.revokeObjectURL(
      url
    );

  } catch {
    window.alert(
      "No fue posible descargar el archivo."
    );
  }
}


function cerrarModal() {
  mostrarModal.value = false;

  detalle.value = null;
  archivoSeleccionado.value = null;
  observaciones.value = "";
}


function codigoEntrega(
  solicitud
) {
  let anio = "";

  if (
    solicitud.fecha_limite
  ) {
    anio =
      new Date(
        solicitud.fecha_limite
      ).getFullYear();
  }

  return (
    `ENT-${anio || "0000"}-`
    + String(
      solicitud.id_destinatario
      || solicitud.id_solicitud
      || 0
    ).padStart(
      3,
      "0"
    )
  );
}


function textoPrioridad(valor) {
  return valor === "alta"
    ? "Alta"
    : "Normal";
}


function formatearFecha(valor) {
  if (!valor) {
    return "—";
  }

  return new Date(valor)
    .toLocaleDateString(
      "es-GT",
      {
        day: "2-digit",
        month: "short",
        year: "numeric",
      }
    );
}


onMounted(
  cargarCorrecciones
);
</script>