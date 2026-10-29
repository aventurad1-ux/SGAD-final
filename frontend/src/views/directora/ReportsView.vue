<template>
  <div class="director-layout">
    <DirectorSidebar />

    <div class="director-main">
      <DirectorTopbar />

      <main class="director-content">
        <section class="reports-page">
          <header class="reports-header">
            <p class="reports-eyebrow">ANÁLISIS INSTITUCIONAL</p>
            <h1>Reportes</h1>
            <p>Configure los filtros, revise una vista previa y después exporte.</p>
          </header>

          <!-- FILTROS -->
          <div class="reports-card no-print">
            <div class="filters">
              <label>
                <span class="field-label">
                  Tipo de reporte
                  <span class="report-required">*</span>
                </span>

                <select
                  v-model="tipoReporte"
                  @change="cambiarTipoReporte"
                >
                  <option value="matriculas">Matrículas por grado</option>
                  <option value="expedientes">Estado de expedientes</option>
                  <option value="inventario">Inventario documental</option>
                  <option value="cumplimiento">Cumplimiento de entregas</option>
                </select>
              </label>

              <label>
                Ciclo escolar
                <input
                  type="text"
                  :value="etiquetaCiclo"
                  disabled
                />
              </label>

              <!-- MATRÍCULAS -->
              <template v-if="tipoReporte === 'matriculas'">
                <label>
                  Grado o sección
                  <select
                    v-model="seccionSeleccionada"
                    @change="reiniciarResultado"
                  >
                    <option value="">Todos los grados</option>

                    <option
                      v-for="seccion in secciones"
                      :key="seccion.id_seccion"
                      :value="String(seccion.id_seccion)"
                    >
                      {{ seccion.etiqueta }}
                    </option>
                  </select>
                </label>

                <label>
                  Estado
                  <select
                    v-model="estadoSeleccionado"
                    @change="reiniciarResultado"
                  >
                    <option value="">Todos</option>
                    <option value="Activa">Activa</option>
                    <option value="Promovida">Promovida</option>
                    <option value="Retirada">Retirada</option>
                  </select>
                </label>
              </template>

              <!-- EXPEDIENTES -->
              <template v-else-if="tipoReporte === 'expedientes'">
                <label>
                  Sección
                  <select
                    v-model="seccionSeleccionada"
                    @change="reiniciarResultado"
                  >
                    <option value="">Todas</option>

                    <option
                      v-for="seccion in secciones"
                      :key="seccion.id_seccion"
                      :value="String(seccion.id_seccion)"
                    >
                      {{ seccion.etiqueta }}
                    </option>
                  </select>
                </label>

                <label>
                  Estado del expediente
                  <select
                    v-model="estadoSeleccionado"
                    @change="reiniciarResultado"
                  >
                    <option value="">Todos</option>
                    <option value="Completo">Completo</option>
                    <option value="Incompleto">Incompleto</option>
                  </select>
                </label>
              </template>

              <!-- INVENTARIO DOCUMENTAL -->
              <template v-else-if="tipoReporte === 'inventario'">
                <label>
                  Categoría
                  <select
                    v-model="categoriaSeleccionada"
                    @change="reiniciarResultado"
                  >
                    <option value="">Todas</option>

                    <option
                      v-for="categoria in categoriasDisponibles"
                      :key="categoria"
                      :value="categoria"
                    >
                      {{ categoria }}
                    </option>
                  </select>
                </label>

                <div class="reports-date-filters">
                  <label>
                    Desde
                    <input
                      v-model="fechaDesde"
                      type="date"
                      @change="reiniciarResultado"
                    />
                  </label>

                  <label>
                    Hasta
                    <input
                      v-model="fechaHasta"
                      type="date"
                      @change="reiniciarResultado"
                    />
                  </label>
                </div>
              </template>

              <!-- CUMPLIMIENTO -->
              <template v-else-if="tipoReporte === 'cumplimiento'">
                <label>
                  Solicitud
                  <select
                    v-model="solicitudFiltro"
                    @change="reiniciarResultado"
                  >
                    <option value="">Todas las solicitudes</option>

                    <option
                      v-for="solicitud in solicitudesCatalogo"
                      :key="solicitud.id_solicitud"
                      :value="String(solicitud.id_solicitud)"
                    >
                      {{ solicitud.titulo }}
                    </option>
                  </select>
                </label>

                <label>
                  Estado
                  <select
                    v-model="estadoSeleccionado"
                    @change="reiniciarResultado"
                  >
                    <option value="">Todos</option>
                    <option value="pendiente">Pendiente</option>
                    <option value="recibido">Recibido</option>
                    <option value="aprobado">Aprobado</option>
                    <option value="correccion_solicitada">
                      Corrección solicitada
                    </option>
                    <option value="vencido">Vencido</option>
                  </select>
                </label>
              </template>
            </div>

            <div class="reports-actions">
              <button
                type="button"
                :disabled="cargando"
                @click="generarVistaPrevia"
              >
                {{ cargando ? 'Consultando...' : 'Generar vista previa' }}
              </button>
            </div>

            <p v-if="error" class="error-message" role="alert">
              {{ error }}
            </p>
          </div>

          <!-- DOCUMENTO DEL REPORTE -->
          <div
            v-if="vistaPreviaGenerada"
            class="reports-card reports-result institutional-report"
          >
            <div class="report-document-heading">
              <img
                :src="logoEscuela"
                alt="Escudo de la escuela"
                class="report-school-logo"
              />

              <div>
                <h2>{{ tituloReporte }}</h2>

                <p>
                  EORM Orfelinda Osorio Lemus ·
                  {{ etiquetaCiclo }} ·
                  Generado {{ fechaGeneracion }}
                </p>
              </div>
            </div>

            <div class="report-document-rule"></div>

            <p class="report-record-count">
              {{ filasReporte.length }}
              {{ filasReporte.length === 1
                ? 'registro encontrado.'
                : 'registros encontrados.' }}
            </p>

            <div class="table-scroll">
              <!-- MATRÍCULAS -->
              <table
                v-if="tipoReporte === 'matriculas'"
                class="report-document-table"
              >
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Estudiante</th>
                    <th>Sección</th>
                    <th>Docente</th>
                    <th>Estado</th>
                  </tr>
                </thead>

                <tbody>
                  <tr
                    v-for="fila in filasReporte"
                    :key="fila.id_matricula"
                  >
                    <td>{{ fila.codigo || '—' }}</td>
                    <td>{{ fila.nombre }}</td>
                    <td>{{ fila.seccion || 'Sin sección' }}</td>
                    <td>{{ docenteDeEstudiante(fila) }}</td>
                    <td>{{ fila.estado || 'Activa' }}</td>
                  </tr>

                  <tr v-if="!filasReporte.length">
                    <td colspan="5" class="empty-row">
                      No se encontraron matrículas para los filtros seleccionados.
                    </td>
                  </tr>
                </tbody>
              </table>

              <!-- EXPEDIENTES -->
              <table
                v-else-if="tipoReporte === 'expedientes'"
                class="report-document-table"
              >
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Estudiante</th>
                    <th>Sección</th>
                    <th>Estado</th>
                    <th>Documentos faltantes</th>
                  </tr>
                </thead>

                <tbody>
                  <tr
                    v-for="fila in filasReporte"
                    :key="fila.id_matricula"
                  >
                    <td>{{ fila.codigo || '—' }}</td>
                    <td>{{ fila.nombre }}</td>
                    <td>{{ fila.seccion || 'Sin sección' }}</td>
                    <td>{{ estadoExpediente(fila) }}</td>
                    <td>{{ documentosFaltantes(fila) }}</td>
                  </tr>

                  <tr v-if="!filasReporte.length">
                    <td colspan="5" class="empty-row">
                      No hay expedientes para los filtros seleccionados.
                    </td>
                  </tr>
                </tbody>
              </table>

              <!-- INVENTARIO -->
              <table
                v-else-if="tipoReporte === 'inventario'"
                class="report-document-table"
              >
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Título</th>
                    <th>Categoría</th>
                    <th>Responsable</th>
                    <th>Fecha</th>
                    <th>Estado</th>
                    <th>Archivo</th>
                  </tr>
                </thead>

                <tbody>
                  <tr
                    v-for="fila in filasReporte"
                    :key="fila.id_entrega"
                  >
                    <td>{{ fila.codigo || '—' }}</td>
                    <td>{{ fila.solicitud || 'Sin título' }}</td>
                    <td>{{ fila.categoria || 'Sin categoría' }}</td>
                    <td>{{ fila.docente || 'Sin nombre' }}</td>
                    <td>{{ fila.fecha || '—' }}</td>
                    <td>{{ etiquetaEstado(fila.estado) }}</td>
                    <td>{{ fila.archivo || '—' }}</td>
                  </tr>

                  <tr v-if="!filasReporte.length">
                    <td colspan="7" class="empty-row">
                      No hay documentos para los filtros seleccionados.
                    </td>
                  </tr>
                </tbody>
              </table>

              <!-- CUMPLIMIENTO -->
              <table
                v-else
                class="report-document-table report-compliance-table"
              >
                <thead>
                  <tr>
                    <th>Solicitud</th>
                    <th>Docente</th>
                    <th>Secciones</th>
                    <th>Fecha límite</th>
                    <th>Fecha entrega</th>
                    <th>Estado</th>
                    <th>Código</th>
                  </tr>
                </thead>

                <tbody>
                  <tr
                    v-for="fila in filasReporte"
                    :key="`${fila.id_solicitud}-${fila.id_destinatario}`"
                  >
                    <td>{{ fila.titulo }}</td>
                    <td>{{ fila.docente || 'Sin nombre' }}</td>
                    <td>{{ fila.alcance || 'Sin sección' }}</td>
                    <td>{{ formatearFecha(fila.fecha_limite) }}</td>
                    <td>
                      {{ fila.fecha
                        ? formatearFechaHora(fila.fecha)
                        : '—' }}
                    </td>
                    <td>{{ etiquetaEstadoEntrega(fila) }}</td>
                    <td>{{ codigoEntrega(fila) }}</td>
                  </tr>

                  <tr v-if="!filasReporte.length">
                    <td colspan="7" class="empty-row">
                      No se encontraron entregas para los filtros seleccionados.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="report-document-actions no-print">
              <button
                type="button"
                class="button-secondary"
                :disabled="!filasReporte.length"
                @click="exportarCSV"
              >
                Exportar CSV
              </button>

              <button
                type="button"
                @click="imprimirPDF"
              >
                Imprimir / Guardar PDF
              </button>
            </div>

            <p
              v-if="tipoReporte === 'inventario'"
              class="reports-footnote no-print"
            >
              Alcance actual: archivos de entregas docentes registrados
              en la bandeja de revisión. La consulta del repositorio
              institucional está pendiente de integración.
            </p>

            <p
              v-if="tipoReporte === 'cumplimiento'"
              class="reports-footnote no-print"
            >
              Las secciones y los códigos institucionales se mostrarán
              cuando estén disponibles en la consulta del backend.
            </p>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';

import DirectorSidebar from '../../components/layout/DirectorSidebar.vue';
import DirectorTopbar from '../../components/layout/DirectorTopbar.vue';

import {
  obtenerSolicitudes,
  obtenerCatalogosSolicitudes,
  obtenerCumplimiento
} from '../../services/requestsService';

import api from '../../services/api';
import logoEscuela from '../../assets/images/logo.jpeg';

import './reports.css';

/* =========================================================
   ESTADO
========================================================= */

const tipoReporte = ref('matriculas');

const ciclos = ref([]);
const cicloSeleccionado = ref('');

const secciones = ref([]);
const estudiantes = ref([]);

const seccionSeleccionada = ref('');
const estadoSeleccionado = ref('');

const solicitudesCatalogo = ref([]);
const solicitudFiltro = ref('');

const categoriaSeleccionada = ref('');
const fechaDesde = ref('');
const fechaHasta = ref('');

const inventarioBase = ref([]);
const cumplimientoBase = ref([]);

const vistaPreviaGenerada = ref(false);
const cargando = ref(false);
const error = ref('');
const fechaGeneracion = ref('');

/* =========================================================
   CICLO ESCOLAR
========================================================= */

const cicloActual = computed(() => {
  return ciclos.value.find(
    ciclo =>
      String(ciclo.id_ciclo) === String(cicloSeleccionado.value)
  ) || null;
});

const etiquetaCiclo = computed(() => {
  if (!cicloActual.value) return 'Ciclo no disponible';

  const estado = String(cicloActual.value.estado || '')
    .toLowerCase();

  return `Ciclo ${cicloActual.value.anio} · ${
    estado === 'activo' ? 'Actual' : 'Cerrado'
  }`;
});

/*
  El ciclo se obtiene del backend, no del selector visual
  provisional de DirectorTopbar.vue.

  Cuando se integre el selector global, este valor deberá
  provenir del estado compartido del sistema.
*/

/* =========================================================
   NOMBRE DEL REPORTE
========================================================= */

const tituloReporte = computed(() => {
  const titulos = {
    matriculas: 'Reporte de matrículas',
    expedientes: 'Reporte de estado de expedientes',
    inventario: 'Inventario documental',
    cumplimiento: 'Cumplimiento de entregas'
  };

  return titulos[tipoReporte.value] || 'Reporte';
});

/* =========================================================
   ESTADOS Y FORMATOS
========================================================= */

function etiquetaEstado(estado) {
  const etiquetas = {
    pendiente: 'Pendiente',
    vencido: 'Vencido',
    recibido: 'Recibido',
    entregado: 'Entregado',
    en_revision: 'En revisión',
    correccion_solicitada: 'Corrección solicitada',
    aprobado: 'Aprobado',
    rechazado: 'Rechazado'
  };

  const clave = String(estado || '').toLowerCase();

  return etiquetas[clave] || estado || 'Sin estado';
}

function etiquetaEstadoEntrega(fila) {
  return etiquetaEstado(
    fila.estado ||
    (fila.id_entrega != null ? 'entregado' : 'pendiente')
  );
}

function estadoParaFiltroEntrega(fila) {
  const estado = String(fila.estado || '').toLowerCase();

  if (estado === 'entregado' || estado === 'en_revision') {
    return 'recibido';
  }

  return estado ||
    (fila.id_entrega != null ? 'recibido' : 'pendiente');
}

function estadoExpediente(estudiante) {
  return estudiante.expediente?.completo
    ? 'Completo'
    : 'Incompleto';
}

function documentosFaltantes(estudiante) {
  const expediente = estudiante.expediente || {};

  if (
    expediente.total == null ||
    expediente.entregados == null
  ) {
    return 'No disponible';
  }

  const total = Number(expediente.total);
  const entregados = Number(expediente.entregados);

  if (!Number.isFinite(total) || !Number.isFinite(entregados)) {
    return 'No disponible';
  }

  return String(Math.max(0, total - entregados));
}

function formatearFecha(valor) {
  if (!valor) return '—';

  const texto = String(valor);

  if (/^\d{4}-\d{2}-\d{2}$/.test(texto)) {
    const [anio, mes, dia] = texto.split('-');
    return `${dia}/${mes}/${anio}`;
  }

  const fecha = new Date(valor);

  if (Number.isNaN(fecha.getTime())) {
    return 'Fecha no válida';
  }

  return fecha.toLocaleDateString('es-GT', {
    timeZone: 'America/Guatemala',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
}

function formatearFechaHora(valor) {
  if (!valor) return '—';

  const fecha = new Date(valor);

  if (Number.isNaN(fecha.getTime())) {
    return 'Fecha no válida';
  }

  return fecha.toLocaleString('es-GT', {
    timeZone: 'America/Guatemala',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function fechaISO(valor) {
  if (!valor) return '';

  const texto = String(valor);

  if (/^\d{4}-\d{2}-\d{2}/.test(texto)) {
    return texto.slice(0, 10);
  }

  return '';
}

/* =========================================================
   UTILIDADES
========================================================= */

function mensajeError(err, defecto) {
  if (err.response?.status === 401) {
    return 'La sesión expiró o no es válida. Cierre sesión y vuelva a iniciar.';
  }

  if (err.response?.status === 403) {
    return 'Su cuenta no tiene permiso para consultar este reporte.';
  }

  return (
    err.response?.data?.mensaje ||
    err.response?.data?.error ||
    err.message ||
    defecto
  );
}

function idSolicitudDeCodigo(codigo) {
  const coincidencia = String(codigo || '')
    .match(/^SOL-(\d+)$/i);

  return coincidencia ? Number(coincidencia[1]) : null;
}

function docenteDeEstudiante(estudiante) {
  const seccion = secciones.value.find(
    s => String(s.id_seccion) === String(estudiante.id_seccion)
  );

  return seccion?.docente || 'Sin asignar';
}

function codigoEntrega(fila) {
  if (fila.codigo) return fila.codigo;

  if (fila.id_entrega != null) {
    return `ID ${fila.id_entrega}`;
  }

  return '—';
}

function reiniciarResultado() {
  vistaPreviaGenerada.value = false;
  error.value = '';
}

function cambiarTipoReporte() {
  seccionSeleccionada.value = '';
  estadoSeleccionado.value = '';
  solicitudFiltro.value = '';
  categoriaSeleccionada.value = '';
  fechaDesde.value = '';
  fechaHasta.value = '';

  inventarioBase.value = [];
  cumplimientoBase.value = [];

  reiniciarResultado();

  if (
    tipoReporte.value === 'matriculas' ||
    tipoReporte.value === 'expedientes'
  ) {
    cargarDatosEscolares();
  }

  if (tipoReporte.value === 'cumplimiento') {
    cargarSolicitudes();
  }

  if (tipoReporte.value === 'inventario') {
    cargarSolicitudes();
  }
}

/* =========================================================
   CARGA DE CATÁLOGOS
========================================================= */

async function cargarCiclos() {
  try {
    const resultado = await obtenerCatalogosSolicitudes();

    ciclos.value = Array.isArray(resultado.ciclos)
      ? resultado.ciclos
      : [];

    const activo = ciclos.value.find(
      ciclo => String(ciclo.estado).toLowerCase() === 'activo'
    );

    const elegido = activo || ciclos.value[0];

    cicloSeleccionado.value = elegido
      ? String(elegido.id_ciclo)
      : '';
  } catch (err) {
    error.value = mensajeError(
      err,
      'No fue posible cargar los ciclos escolares.'
    );
  }
}

async function cargarSolicitudes() {
  try {
    const resultado = await obtenerSolicitudes(
      cicloSeleccionado.value
        ? Number(cicloSeleccionado.value)
        : null
    );

    solicitudesCatalogo.value = Array.isArray(resultado.solicitudes)
      ? resultado.solicitudes
      : [];
  } catch (err) {
    console.error('Error al consultar solicitudes:', err);
    solicitudesCatalogo.value = [];
  }
}

async function cargarDatosEscolares() {
  if (!cicloSeleccionado.value) {
    secciones.value = [];
    estudiantes.value = [];
    return;
  }

  try {
    const respuesta = await api.get('/directora/expedientes', {
      params: {
        id_ciclo: Number(cicloSeleccionado.value)
      }
    });

    secciones.value = Array.isArray(respuesta.data?.secciones)
      ? respuesta.data.secciones
      : [];

    estudiantes.value = Array.isArray(respuesta.data?.estudiantes)
      ? respuesta.data.estudiantes
      : [];
  } catch (err) {
    secciones.value = [];
    estudiantes.value = [];

    error.value = mensajeError(
      err,
      'No fue posible cargar las secciones y matrículas.'
    );
  }
}

/* =========================================================
   FILTROS: MATRÍCULAS Y EXPEDIENTES
========================================================= */

const filasEscolares = computed(() => {
  return estudiantes.value.filter(estudiante => {
    const coincideSeccion =
      !seccionSeleccionada.value ||
      String(estudiante.id_seccion) ===
      seccionSeleccionada.value;

    if (!coincideSeccion) return false;

    if (tipoReporte.value === 'matriculas') {
      const estado = String(
        estudiante.estado || 'Activa'
      ).toLowerCase();

      return (
        !estadoSeleccionado.value ||
        estado === estadoSeleccionado.value.toLowerCase()
      );
    }

    if (tipoReporte.value === 'expedientes') {
      return (
        !estadoSeleccionado.value ||
        estadoExpediente(estudiante) === estadoSeleccionado.value
      );
    }

    return true;
  });
});

/* =========================================================
   FILTROS: INVENTARIO
========================================================= */

const categoriasDisponibles = computed(() => {
  return [
    ...new Set(
      inventarioBase.value
        .map(fila => fila.categoria)
        .filter(Boolean)
    )
  ].sort((a, b) => a.localeCompare(b, 'es'));
});

const filasInventario = computed(() => {
  return inventarioBase.value.filter(fila => {
    const coincideCategoria =
      !categoriaSeleccionada.value ||
      fila.categoria === categoriaSeleccionada.value;

    const fecha = fechaISO(fila.fechaOriginal);

    const coincideDesde =
      !fechaDesde.value ||
      (fecha && fecha >= fechaDesde.value);

    const coincideHasta =
      !fechaHasta.value ||
      (fecha && fecha <= fechaHasta.value);

    return coincideCategoria && coincideDesde && coincideHasta;
  });
});

/* =========================================================
   FILTROS: CUMPLIMIENTO
========================================================= */

const filasCumplimiento = computed(() => {
  return cumplimientoBase.value.filter(fila => {
    const coincideSolicitud =
      !solicitudFiltro.value ||
      String(fila.id_solicitud) === solicitudFiltro.value;

    const coincideEstado =
      !estadoSeleccionado.value ||
      estadoParaFiltroEntrega(fila) === estadoSeleccionado.value;

    return coincideSolicitud && coincideEstado;
  });
});

const filasReporte = computed(() => {
  if (
    tipoReporte.value === 'matriculas' ||
    tipoReporte.value === 'expedientes'
  ) {
    return filasEscolares.value;
  }

  if (tipoReporte.value === 'inventario') {
    return filasInventario.value;
  }

  return filasCumplimiento.value;
});

/* =========================================================
   GENERAR VISTA PREVIA
========================================================= */

async function generarVistaPrevia() {
  error.value = '';
  vistaPreviaGenerada.value = false;

  if (!cicloSeleccionado.value) {
    error.value = 'No existe un ciclo escolar disponible.';
    return;
  }

  if (
    tipoReporte.value === 'inventario' &&
    fechaDesde.value &&
    fechaHasta.value &&
    fechaDesde.value > fechaHasta.value
  ) {
    error.value = 'La fecha inicial no puede ser posterior a la fecha final.';
    return;
  }

  cargando.value = true;

  try {
    if (
      tipoReporte.value === 'matriculas' ||
      tipoReporte.value === 'expedientes'
    ) {
      await cargarDatosEscolares();

      /*
        La ruta actual de Expedientes devuelve matrículas
        activas. Los demás estados requieren ampliar
        la consulta en Flask.
      */
    }

    else if (tipoReporte.value === 'inventario') {
      const [respuestaEntregas, respuestaSolicitudes] =
        await Promise.all([
          api.get('/directora/revision'),
          obtenerSolicitudes(Number(cicloSeleccionado.value))
        ]);

      const entregas = respuestaEntregas.data?.entregas;
      const solicitudes = respuestaSolicitudes?.solicitudes;

      if (!Array.isArray(entregas) || !Array.isArray(solicitudes)) {
        throw new Error('Respuesta de inventario inesperada.');
      }

      const mapaSolicitudes = new Map(
        solicitudes.map(s => [
          Number(s.id_solicitud),
          s
        ])
      );

      inventarioBase.value = entregas
        .filter(entrega => {
          const id = idSolicitudDeCodigo(entrega.codigo);

          return (
            entrega.archivo &&
            id != null &&
            mapaSolicitudes.has(id)
          );
        })
        .map(entrega => {
          const id = idSolicitudDeCodigo(entrega.codigo);
          const solicitud = mapaSolicitudes.get(id);

          return {
            ...entrega,
            categoria:
              solicitud?.categoria?.nombre ||
              solicitud?.categoria ||
              '',
            fechaOriginal: entrega.fecha || '',
            fecha: entrega.fecha || ''
          };
        });
    }

    else if (tipoReporte.value === 'cumplimiento') {
      const resultado = await obtenerSolicitudes(
        Number(cicloSeleccionado.value)
      );

      if (!Array.isArray(resultado.solicitudes)) {
        throw new Error('Respuesta de solicitudes inesperada.');
      }

      solicitudesCatalogo.value = resultado.solicitudes;

      const solicitudesElegidas = resultado.solicitudes.filter(
        solicitud =>
          !solicitudFiltro.value ||
          String(solicitud.id_solicitud) === solicitudFiltro.value
      );

      const respuestas = await Promise.all(
        solicitudesElegidas.map(async solicitud => {
          const resultadoCumplimiento =
            await obtenerCumplimiento(solicitud.id_solicitud);

          if (!Array.isArray(resultadoCumplimiento.cumplimiento)) {
            throw new Error('Respuesta de cumplimiento inesperada.');
          }

          return resultadoCumplimiento.cumplimiento.map(fila => ({
            ...fila,
            id_solicitud: solicitud.id_solicitud,
            titulo: solicitud.titulo,
            fecha_limite: solicitud.fecha_limite
          }));
        })
      );

      cumplimientoBase.value = respuestas.flat();
    }

    fechaGeneracion.value = new Date().toLocaleString('es-GT', {
      timeZone: 'America/Guatemala',
      dateStyle: 'short',
      timeStyle: 'short'
    });

    vistaPreviaGenerada.value = true;
  } catch (err) {
    error.value = mensajeError(
      err,
      'No fue posible generar el reporte. Revise la conexión con Flask.'
    );

    vistaPreviaGenerada.value = false;
  } finally {
    cargando.value = false;
  }
}

/* =========================================================
   EXPORTACIÓN CSV
========================================================= */

function campoCSV(valor) {
  let texto = String(valor ?? '');

  // Evitar que Excel ejecute fórmulas recibidas de la BD.
  if (/^\s*[=+@-]/.test(texto)) {
    texto = "'" + texto;
  }

  return `"${texto.replace(/"/g, '""')}"`;
}

function exportarCSV() {
  if (!filasReporte.value.length) return;

  let columnas = [];
  let registros = [];
  let nombreArchivo = '';

  if (tipoReporte.value === 'matriculas') {
    columnas = [
      'Código', 'Estudiante', 'Sección', 'Docente', 'Estado'
    ];

    registros = filasReporte.value.map(e => [
      e.codigo,
      e.nombre,
      e.seccion,
      docenteDeEstudiante(e),
      e.estado || 'Activa'
    ]);

    nombreArchivo = 'sgad-matriculas.csv';
  }

  else if (tipoReporte.value === 'expedientes') {
    columnas = [
      'Código', 'Estudiante', 'Sección',
      'Estado', 'Documentos faltantes'
    ];

    registros = filasReporte.value.map(e => [
      e.codigo,
      e.nombre,
      e.seccion,
      estadoExpediente(e),
      documentosFaltantes(e)
    ]);

    nombreArchivo = 'sgad-expedientes.csv';
  }

  else if (tipoReporte.value === 'inventario') {
    columnas = [
      'Código', 'Título', 'Categoría', 'Responsable',
      'Fecha', 'Estado', 'Archivo'
    ];

    registros = filasReporte.value.map(e => [
      e.codigo,
      e.solicitud,
      e.categoria,
      e.docente,
      e.fecha,
      etiquetaEstado(e.estado),
      e.archivo
    ]);

    nombreArchivo = 'sgad-inventario.csv';
  }

  else {
    columnas = [
      'Solicitud', 'Docente', 'Secciones',
      'Fecha límite', 'Fecha entrega', 'Estado', 'Código'
    ];

    registros = filasReporte.value.map(e => [
      e.titulo,
      e.docente,
      e.alcance || 'Sin sección',
      formatearFecha(e.fecha_limite),
      e.fecha ? formatearFechaHora(e.fecha) : '',
      etiquetaEstadoEntrega(e),
      codigoEntrega(e)
    ]);

    nombreArchivo = 'sgad-cumplimiento-entregas.csv';
  }

  const contenido =
    '\uFEFF' +
    [columnas, ...registros]
      .map(fila => fila.map(campoCSV).join(';'))
      .join('\r\n');

  const url = URL.createObjectURL(
    new Blob([contenido], {
      type: 'text/csv;charset=utf-8;'
    })
  );

  const enlace = document.createElement('a');

  enlace.href = url;
  enlace.download = nombreArchivo;

  document.body.appendChild(enlace);
  enlace.click();
  enlace.remove();

  setTimeout(() => URL.revokeObjectURL(url), 0);
}

/* =========================================================
   PDF
========================================================= */

function imprimirPDF() {
  window.print();
}

/* =========================================================
   INICIALIZACIÓN
========================================================= */

onMounted(async () => {
  await cargarCiclos();

  if (cicloSeleccionado.value) {
    await Promise.all([
      cargarDatosEscolares(),
      cargarSolicitudes()
    ]);
  }
});
</script>