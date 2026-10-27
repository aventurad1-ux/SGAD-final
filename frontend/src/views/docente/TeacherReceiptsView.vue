<template>
  <div class="teacher-page">
    <TeacherSidebar />

    <main class="teacher-main">
      <TeacherTopbar />

      <section class="receipts-page">
        <header class="receipts-header">
          <p class="receipts-kicker">
            ESPACIO DOCENTE
          </p>

          <h1>Mis comprobantes</h1>

          <p class="receipts-subtitle">
            Constancias generadas al realizar una entrega.
          </p>
        </header>

        <div class="receipts-table-card">
          <div
            v-if="cargando"
            class="receipts-message"
          >
            Cargando comprobantes...
          </div>

          <div
            v-else-if="error"
            class="receipts-message"
          >
            {{ error }}
          </div>

          <div
            v-else-if="!comprobantes.length"
            class="receipts-message"
          >
            No hay comprobantes disponibles.
          </div>

          <table
            v-else
            class="receipts-table"
          >
            <thead>
              <tr>
                <th>CÓDIGO</th>
                <th>SOLICITUD</th>
                <th>FECHA</th>
                <th>ESTADO</th>
                <th>COMPROBANTE</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="comprobante in comprobantes"
                :key="comprobante.id_entrega"
              >
                <td>
                  <strong class="receipt-code">
                    {{ codigoComprobante(comprobante) }}
                  </strong>
                </td>

                <td>
                  {{ comprobante.documento }}
                </td>

                <td>
                  {{
                    formatearFechaHora(
                      comprobante.fecha_actualizacion
                      || comprobante.fecha_primera_entrega
                    )
                  }}
                </td>

                <td>
                  <span
                    class="receipt-status"
                    :class="claseEstado(comprobante.estado)"
                  >
                    {{ textoEstado(comprobante.estado) }}
                  </span>
                </td>

                <td>
                  <button
                    type="button"
                    class="receipt-view-button"
                    @click="abrirComprobante(comprobante)"
                  >
                    Ver / imprimir
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>

    <!-- =====================================================
         MODAL COMPROBANTE
    ====================================================== -->

    <div
      v-if="mostrarModal"
      class="receipt-overlay"
      @click.self="cerrarModal"
    >
      <section
        id="comprobante-imprimible"
        class="receipt-modal"
      >
        <header class="receipt-modal-header">
          <div>
            <p>
              COMPROBANTE DE ENTREGA
            </p>

            <h2>
              {{ codigoComprobante(seleccionado) }}
            </h2>
          </div>

          <button
            type="button"
            class="receipt-close-x no-print"
            @click="cerrarModal"
          >
            ×
          </button>
        </header>

        <div class="receipt-body">
          <div class="receipt-brand">
            <img
              src="../../assets/images/logo.jpeg"
              alt="Logo de la escuela"
            />

            <div>
              <strong>SGAD</strong>
              <span>
                EORM Orfelinda Osorio Lemus
              </span>
            </div>
          </div>

          <div class="receipt-blue-line"></div>

          <div class="receipt-info-grid">
            <div class="receipt-info">
              <span>DOCENTE</span>

              <strong>
                {{ nombreDocente }}
              </strong>
            </div>

            <div class="receipt-info">
              <span>SOLICITUD</span>

              <strong>
                {{ seleccionado?.documento }}
              </strong>
            </div>

            <div class="receipt-info">
              <span>FECHA Y HORA</span>

              <strong>
                {{
                  formatearFechaHora(
                    seleccionado?.fecha_actualizacion
                    || seleccionado?.fecha_primera_entrega
                  )
                }}
              </strong>
            </div>

            <div class="receipt-info">
              <span>ARCHIVO</span>

              <strong>
                {{
                  seleccionado?.ultima_version?.nombre_archivo
                  || "Sin archivo"
                }}
              </strong>
            </div>

            <div class="receipt-info">
              <span>VERSIÓN</span>

              <strong>
                v{{
                  seleccionado?.ultima_version?.numero_version
                  || 1
                }}
              </strong>
            </div>

            <div class="receipt-info">
              <span>ESTADO</span>

              <strong>
                {{ textoEstado(seleccionado?.estado) }}
              </strong>
            </div>
          </div>
        </div>

        <footer class="receipt-modal-footer no-print">
          <button
            type="button"
            class="receipt-footer-button secondary"
            @click="cerrarModal"
          >
            Cerrar
          </button>

          <button
            type="button"
            class="receipt-footer-button primary"
            @click="imprimirComprobante"
          >
            Imprimir / Guardar PDF
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
  obtenerDocumentosDocente,
} from "../../services/docenteDocumentosService";

import "../../assets/css/teacher-receipts.css";


const comprobantes = ref([]);
const seleccionado = ref(null);

const cargando = ref(true);
const error = ref("");

const mostrarModal = ref(false);


const nombreDocente = computed(() => {
  try {
    const usuario =
      JSON.parse(
        localStorage.getItem("usuario")
        || "{}"
      );

    const nombre =
      [
        usuario.nombres,
        usuario.apellidos,
      ]
        .filter(Boolean)
        .join(" ")
        .trim();

    return nombre || "Docente";
  } catch {
    return "Docente";
  }
});


async function cargarComprobantes() {
  cargando.value = true;
  error.value = "";

  try {
    const data =
      await obtenerDocumentosDocente();

    comprobantes.value =
      data.documentos || [];
  } catch (err) {
    error.value =
      err.response?.data?.mensaje
      || "No fue posible cargar los comprobantes.";
  } finally {
    cargando.value = false;
  }
}


function abrirComprobante(comprobante) {
  seleccionado.value =
    comprobante;

  mostrarModal.value =
    true;
}


function cerrarModal() {
  mostrarModal.value =
    false;

  seleccionado.value =
    null;
}


function imprimirComprobante() {
  window.print();
}


function codigoComprobante(comprobante) {
  if (!comprobante) {
    return "";
  }

  let anio = "";

  const fecha =
    comprobante.fecha_primera_entrega
    || comprobante.fecha_actualizacion;

  if (fecha) {
    anio =
      new Date(fecha)
        .getFullYear();
  }

  return (
    `ENT-${anio || "0000"}-`
    + String(
      comprobante.id_entrega || 0
    ).padStart(3, "0")
  );
}


function textoEstado(estado) {
  const estados = {
    pendiente:
      "Pendiente",

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
  };

  return estados[estado]
    || estado
    || "—";
}


function claseEstado(estado) {
  return {
    "status-approved":
      estado === "aprobado",

    "status-correction":
      estado === "correccion_solicitada",

    "status-review":
      estado === "en_revision"
      || estado === "entregado",

    "status-rejected":
      estado === "rechazado",
  };
}


function formatearFechaHora(valor) {
  if (!valor) {
    return "—";
  }

  const fecha =
    new Date(valor);

  const fechaTexto =
    fecha.toLocaleDateString(
      "es-GT",
      {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      }
    );

  const horaTexto =
    fecha.toLocaleTimeString(
      "es-GT",
      {
        hour: "2-digit",
        minute: "2-digit",
        hour12: true,
      }
    );

  return `${fechaTexto}, ${horaTexto}`;
}


onMounted(
  cargarComprobantes
);
</script>