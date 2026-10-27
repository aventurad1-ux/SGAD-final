<template>
  <div class="teacher-page">
    <TeacherSidebar />

    <main class="teacher-main">
      <TeacherTopbar />

      <section class="requests-page">
        <header class="requests-header">
          <p class="requests-kicker">
            ESPACIO DOCENTE
          </p>

          <h1>Entregas solicitadas</h1>

          <p class="requests-subtitle">
            Documentos requeridos por Dirección en el ciclo seleccionado.
          </p>
        </header>

        <div
          v-if="error"
          class="requests-empty"
        >
          {{ error }}
        </div>

        <div
          v-else-if="cargando"
          class="requests-empty"
        >
          Cargando solicitudes...
        </div>

        <div
          v-else-if="!solicitudes.length"
          class="requests-empty"
        >
          No tienes solicitudes asignadas para este ciclo.
        </div>

        <div
          v-else
          class="requests-list"
        >
          <article
            v-for="solicitud in solicitudes"
            :key="solicitud.id_destinatario"
            class="request-card"
          >
            <div class="request-card-top">
              <div>
                <h2>
                  {{ solicitud.titulo }}
                </h2>

                <p class="request-deadline">
                  Vence {{ formatearFecha(solicitud.fecha_limite) }}
                </p>
              </div>

              <span
                class="request-status"
                :class="`status-${solicitud.estado}`"
              >
                {{ textoEstado(solicitud.estado) }}
              </span>
            </div>

            <p class="request-description">
              {{ solicitud.descripcion }}
            </p>

            <div class="request-card-footer">
              <p>
                Formatos:
                {{
                  solicitud.formatos_permitidos?.length
                    ? solicitud.formatos_permitidos.join(", ")
                    : "Sin especificar"
                }}
              </p>

              <button
                type="button"
                @click="abrirSolicitud(solicitud)"
              >
                {{ textoAccion(solicitud) }}
              </button>
            </div>
          </article>
        </div>
      </section>
    </main>

    <!-- =====================================================
         MODAL
    ====================================================== -->

    <div
      v-if="mostrarModal"
      class="request-overlay"
      @click.self="cerrarModal"
    >
      <section class="request-modal">
        <header class="request-modal-header">
          <div>
            <p>SOLICITUD DE DIRECCIÓN</p>

            <h2>
              {{ detalle?.titulo }}
            </h2>
          </div>

          <button
            type="button"
            class="request-modal-close-x"
            @click="cerrarModal"
          >
            ×
          </button>
        </header>

        <div
          v-if="cargandoDetalle"
          class="request-modal-loading"
        >
          Cargando solicitud...
        </div>

        <div
          v-else-if="detalle"
          class="request-modal-body"
        >
          <div class="request-info-grid">
            <div class="request-info-item">
              <span>FECHA LÍMITE</span>

              <strong>
                {{ formatearFecha(detalle.fecha_limite) }}
              </strong>
            </div>

            <div class="request-info-item">
              <span>PRIORIDAD</span>

              <strong>
                {{ textoPrioridad(detalle.prioridad) }}
              </strong>
            </div>

            <div class="request-info-item">
              <span>FORMATOS PERMITIDOS</span>

              <strong>
                {{
                  detalle.formatos_permitidos?.length
                    ? detalle.formatos_permitidos.join(", ")
                    : "Sin especificar"
                }}
              </strong>
            </div>

            <div class="request-info-item">
              <span>ESTADO</span>

              <strong>
                {{ textoEstado(detalle.estado) }}
              </strong>
            </div>
          </div>

          <p class="request-modal-description">
            {{ detalle.descripcion }}
          </p>

          <!-- ==========================
               ENTREGAR
          =========================== -->

          <div
            v-if="
              detalle.accion === 'entregar'
              && requisitoActual
            "
            class="request-upload-area"
          >
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

          <!-- ==========================
               VER ENTREGA
          =========================== -->

          <div
            v-else-if="
              detalle.accion === 'ver_entrega'
              && requisitoActual
            "
          >
            <div
              v-if="ultimaVersion"
              class="request-file-box"
            >
              <span class="request-file-icon">▤</span>

              <span>
                Archivo entregado:
              </span>

              <strong>
                {{ ultimaVersion.nombre_archivo }}
              </strong>

              <span>
                · v{{ ultimaVersion.numero_version || 1 }}
              </span>
            </div>

            <div
              v-if="versionesAnteriores.length"
              class="request-versions"
            >
              <p>Versiones anteriores</p>

              <div
                v-for="version in versionesAnteriores"
                :key="version.id_version_entrega"
                class="request-version-row"
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
              class="request-no-versions"
            >
              No hay versiones anteriores.
            </p>
          </div>
        </div>

        <footer class="request-modal-footer">
          <button
            type="button"
            class="modal-btn modal-btn-light"
            @click="cerrarModal"
          >
            Cerrar
          </button>

          <template
            v-if="
              detalle?.accion === 'ver_entrega'
              && ultimaVersion
            "
          >
            <button
              type="button"
              class="modal-btn modal-btn-view"
              @click="verArchivo"
            >
              Ver archivo
            </button>

            <button
              type="button"
              class="modal-btn modal-btn-light"
              @click="descargarArchivo"
            >
              Descargar
            </button>
          </template>

          <button
            v-if="
              detalle?.accion === 'entregar'
              && requisitoActual
            "
            type="button"
            class="modal-btn modal-btn-primary"
            :disabled="enviando"
            @click="realizarEntrega"
          >
            {{
              enviando
                ? "Enviando..."
                : detalle.estado === "correccion_solicitada"
                  ? "Enviar corrección"
                  : "Realizar entrega"
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

import "../../assets/css/teacher-requests.css";


const route = useRoute();
const router = useRouter();


const solicitudes = ref([]);
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

  if (!versiones.length) {
    return [];
  }

  const ultimaId =
    ultimaVersion.value?.id_version_entrega;

  return versiones.filter(
    (version) =>
      version.id_version_entrega !== ultimaId
  );
});


const acceptArchivo = computed(() => {
  const formatos =
    requisitoActual.value?.formatos_permitidos || [];

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
    formatos.includes("PNG") ||
    formatos.includes("PNG/JPG")
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

  const numero = Number(valor);

  return Number.isNaN(numero)
    ? null
    : numero;
}


async function cargarSolicitudes() {
  cargando.value = true;
  error.value = "";

  try {
    const data =
      await obtenerSolicitudesDocente(
        obtenerIdCiclo()
      );

    solicitudes.value =
      data.solicitudes || [];

    await abrirDesdeQuery();

  } catch (err) {
    error.value =
      err.response?.data?.mensaje
      || "No fue posible cargar las solicitudes.";

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
    || Number.isNaN(idAbrir)
  ) {
    return;
  }

  const solicitud =
    solicitudes.value.find(
      item =>
        Number(
          item.id_destinatario
        ) === idAbrir
    );

  if (!solicitud) {
    return;
  }

  await abrirSolicitud(
    solicitud
  );

  /*
   * Quitamos ?abrir=... después de abrir
   * el modal para evitar que se vuelva
   * a abrir al recargar la página.
   */
  await router.replace({
    path:
      "/docente/solicitudes"
  });
}


async function abrirSolicitud(solicitud) {
  mostrarModal.value = true;
  cargandoDetalle.value = true;

  detalle.value = null;
  archivoSeleccionado.value = null;
  observaciones.value = "";

  try {
    const data =
      await obtenerSolicitudDocente(
        solicitud.id_destinatario
      );

    detalle.value =
      data.solicitud;

  } catch (err) {
    window.alert(
      err.response?.data?.mensaje
      || "No fue posible abrir la solicitud."
    );

    mostrarModal.value = false;

  } finally {
    cargandoDetalle.value = false;
  }
}


function cerrarModal() {
  mostrarModal.value = false;
  detalle.value = null;
  archivoSeleccionado.value = null;
  observaciones.value = "";
}


function seleccionarArchivo(event) {
  archivoSeleccionado.value =
    event.target.files?.[0] || null;
}


async function realizarEntrega() {
  if (
    !detalle.value ||
    !requisitoActual.value
  ) {
    return;
  }

  if (!archivoSeleccionado.value) {
    window.alert(
      "Seleccione un archivo."
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
      detalle.value.estado === "correccion_solicitada"
        ? "Corrección enviada correctamente."
        : "Entrega realizada correctamente."
    );

    cerrarModal();

    await cargarSolicitudes();

    window.dispatchEvent(
      new Event(
        "sgad-actualizar-contadores-docente"
      )
    );

  } catch (err) {
    window.alert(
      err.response?.data?.mensaje
      || "No fue posible realizar la entrega."
    );

  } finally {
    enviando.value = false;
  }
}


async function verArchivo() {
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


async function descargarArchivo() {
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
      || "entrega";

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


function textoAccion(solicitud) {
  if (solicitud.accion === "entregar") {
    return "Entregar";
  }

  if (solicitud.accion === "ver_entrega") {
    return "Ver entrega";
  }

  return "Ver solicitud";
}


function textoEstado(valor) {
  const estados = {
    pendiente:
      "Pendiente",

    vencido:
      "Vencido",

    entregado:
      "Entregado",

    en_revision:
      "En revisión",

    correccion_solicitada:
      "Corrección solicitada",

    aprobado:
      "Aprobado",

    rechazado:
      "Rechazado",

    cerrado:
      "Cerrada",
  };

  return estados[valor] || valor;
}


function textoPrioridad(valor) {
  if (valor === "alta") {
    return "Alta";
  }

  return "Normal";
}


function formatearFecha(valor) {
  if (!valor) {
    return "—";
  }

  const fecha =
    new Date(valor);

  return fecha.toLocaleDateString(
    "es-GT",
    {
      day: "2-digit",
      month: "short",
      year: "numeric",
    }
  );
}


onMounted(
  cargarSolicitudes
);
</script>