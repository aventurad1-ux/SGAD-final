<template>
  <div class="teacher-page">
    <TeacherSidebar />

    <main class="teacher-main">
      <TeacherTopbar />

      <section class="documents-page">
        <header class="documents-header">
          <p class="documents-kicker">
            ESPACIO DOCENTE
          </p>

          <h1>
            Mis documentos
          </h1>

          <p class="documents-subtitle">
            Archivos entregados, versiones y estado de revisión.
          </p>
        </header>

        <div
          v-if="error"
          class="documents-empty"
        >
          {{ error }}
        </div>

        <div
          v-else-if="cargando"
          class="documents-empty"
        >
          Cargando documentos...
        </div>

        <div
          v-else-if="!documentos.length"
          class="documents-empty"
        >
          Aún no tienes documentos entregados.
        </div>

        <div
          v-else
          class="documents-table-wrapper"
        >
          <table class="documents-table">
            <thead>
              <tr>
                <th>DOCUMENTO</th>
                <th>FECHA</th>
                <th>VERSIÓN</th>
                <th>ESTADO</th>
                <th>ACCIONES</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="documento in documentos"
                :key="documento.id_entrega"
              >
                <td>
                  <strong class="document-name">
                    {{ documento.documento }}
                  </strong>

                  <span class="document-code">
                    {{ documento.codigo }}
                  </span>
                </td>

                <td>
                  {{ formatearFechaHora(
                    documento.fecha_actualizacion
                    || documento.fecha_primera_entrega
                  ) }}
                </td>

                <td>
                  v{{
                    documento.ultima_version?.numero_version
                    || 1
                  }}
                </td>

                <td>
                  <span
                    class="document-status"
                    :class="`status-${documento.estado}`"
                  >
                    {{ textoEstado(documento.estado) }}
                  </span>
                </td>

                <td>
                  <div class="document-actions">
                    <button
                      type="button"
                      class="document-btn document-btn-detail"
                      @click="abrirDetalle(documento)"
                    >
                      Ver detalle
                    </button>

                    <button
                      type="button"
                      class="document-btn document-btn-download"
                      @click="descargarDocumento(documento)"
                    >
                      Descargar
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>

    <!-- =====================================================
         MODAL DETALLE
    ====================================================== -->

    <div
      v-if="mostrarModal"
      class="document-overlay"
      @click.self="cerrarModal"
    >
      <section class="document-modal">
        <header class="document-modal-header">
          <div>
            <p>
              SOLICITUD DE DIRECCIÓN
            </p>

            <h2>
              {{ detalle?.documento }}
            </h2>
          </div>

          <button
            type="button"
            class="document-modal-x"
            @click="cerrarModal"
          >
            ×
          </button>
        </header>

        <div
          v-if="cargandoDetalle"
          class="document-modal-loading"
        >
          Cargando detalle...
        </div>

        <div
          v-else-if="detalle"
          class="document-modal-body"
        >
          <div class="document-info-grid">
            <div class="document-info-item">
              <span>
                FECHA LÍMITE
              </span>

              <strong>
                {{ formatearFecha(detalle.fecha_limite) }}
              </strong>
            </div>

            <div class="document-info-item">
              <span>
                PRIORIDAD
              </span>

              <strong>
                {{ textoPrioridad(detalle.prioridad) }}
              </strong>
            </div>

            <div class="document-info-item">
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

            <div class="document-info-item">
              <span>
                ESTADO
              </span>

              <strong>
                {{ textoEstado(detalle.estado) }}
              </strong>
            </div>
          </div>

          <p class="document-modal-description">
            {{ detalle.descripcion }}
          </p>

          <div
            v-if="detalle.ultima_version"
            class="document-file-box"
          >
            <span class="document-file-icon">
              ▤
            </span>

            <span>
              Archivo entregado:
            </span>

            <strong>
              {{ detalle.ultima_version.nombre_archivo }}
            </strong>

            <span>
              · v{{ detalle.ultima_version.numero_version }}
            </span>
          </div>

          <div
            v-if="versionesAnteriores.length"
            class="document-versions"
          >
            <p>
              Versiones anteriores
            </p>

            <div
              v-for="version in versionesAnteriores"
              :key="version.id_version_entrega"
              class="document-version-row"
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
            class="document-no-versions"
          >
            No hay versiones anteriores.
          </p>
        </div>

        <footer class="document-modal-footer">
          <button
            type="button"
            class="document-modal-btn light"
            @click="cerrarModal"
          >
            Cerrar
          </button>

          <button
            v-if="detalle?.ultima_version"
            type="button"
            class="document-modal-btn view"
            @click="verArchivoActual"
          >
            Ver archivo
          </button>

          <button
            v-if="detalle?.ultima_version"
            type="button"
            class="document-modal-btn light"
            @click="descargarArchivoActual"
          >
            Descargar
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

import TeacherSidebar from "../../components/layout/TeacherSidebar.vue";
import TeacherTopbar from "../../components/layout/TeacherTopbar.vue";

import {
  descargarArchivoDocumentoDocente,
  obtenerDetalleDocumentoDocente,
  obtenerDocumentosDocente,
  verArchivoDocumentoDocente,
} from "../../services/docenteDocumentosService";

import "../../assets/css/teacher-documents.css";


const documentos = ref([]);
const cargando = ref(true);
const error = ref("");

const mostrarModal = ref(false);
const cargandoDetalle = ref(false);
const detalle = ref(null);


const versionesAnteriores = computed(() => {
  if (
    !detalle.value?.versiones?.length
    || !detalle.value?.ultima_version
  ) {
    return [];
  }

  const ultimaId =
    detalle.value.ultima_version.id_version_entrega;

  return detalle.value.versiones.filter(
    (version) =>
      version.id_version_entrega !== ultimaId
  );
});


async function cargarDocumentos() {
  cargando.value = true;
  error.value = "";

  try {
    const data =
      await obtenerDocumentosDocente();

    documentos.value =
      data.documentos || [];
  } catch (err) {
    error.value =
      err.response?.data?.mensaje
      || "No fue posible cargar los documentos.";
  } finally {
    cargando.value = false;
  }
}


async function abrirDetalle(documento) {
  mostrarModal.value = true;
  cargandoDetalle.value = true;
  detalle.value = null;

  try {
    const data =
      await obtenerDetalleDocumentoDocente(
        documento.id_entrega
      );

    detalle.value =
      data.documento;
  } catch (err) {
    window.alert(
      err.response?.data?.mensaje
      || "No fue posible abrir el documento."
    );

    mostrarModal.value = false;
  } finally {
    cargandoDetalle.value = false;
  }
}


function cerrarModal() {
  mostrarModal.value = false;
  detalle.value = null;
}


async function descargarDocumento(documento) {
  const version =
    documento.ultima_version;

  if (!version) {
    window.alert(
      "El documento no tiene una versión disponible."
    );

    return;
  }

  await descargarVersion(
    version
  );
}


async function verArchivoActual() {
  const version =
    detalle.value?.ultima_version;

  if (!version) {
    return;
  }

  try {
    const response =
      await verArchivoDocumentoDocente(
        version.id_version_entrega
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
      URL.revokeObjectURL(url);
    }, 60000);
  } catch {
    window.alert(
      "No fue posible abrir el archivo."
    );
  }
}


async function descargarArchivoActual() {
  const version =
    detalle.value?.ultima_version;

  if (!version) {
    return;
  }

  await descargarVersion(
    version
  );
}


async function descargarVersion(version) {
  try {
    const response =
      await descargarArchivoDocumentoDocente(
        version.id_version_entrega
      );

    const url =
      URL.createObjectURL(
        response.data
      );

    const link =
      document.createElement("a");

    link.href = url;

    link.download =
      version.nombre_archivo
      || "documento";

    document.body.appendChild(
      link
    );

    link.click();
    link.remove();

    URL.revokeObjectURL(url);
  } catch {
    window.alert(
      "No fue posible descargar el archivo."
    );
  }
}


function textoEstado(valor) {
  const estados = {
    pendiente: "Pendiente",
    entregado: "Entregado",
    en_revision: "En revisión",
    correccion_solicitada:
      "Corrección solicitada",
    aprobado: "Aprobado",
    rechazado: "Rechazado",
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


function formatearFechaHora(valor) {
  if (!valor) {
    return "—";
  }

  const fecha =
    new Date(valor);

  return fecha.toLocaleString(
    "es-GT",
    {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }
  );
}


onMounted(
  cargarDocumentos
);
</script>