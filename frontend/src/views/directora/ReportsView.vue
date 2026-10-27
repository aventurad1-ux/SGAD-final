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

    <div class="reports-card">
      <div class="filters">
        <label>
          <span class="field-label">Tipo de reporte <span class="report-required">*</span></span>
          <select v-model="tipoReporte" @change="reiniciarVistaPrevia">
            <option value="matriculas">Matrículas por grado</option>
            <option value="expedientes">Estado de expedientes</option>
            <option value="inventario">Inventario documental</option>
            <option value="cumplimiento">Cumplimiento de entregas</option>
          </select>
        </label>

        <label>
          Ciclo escolar
          <select v-model="cicloSeleccionado" @change="reiniciarVistaPrevia">
            <option value="">{{ tipoReporte === 'cumplimiento' || tipoReporte === 'inventario' ? 'Todos los ciclos' : 'Ciclo activo (automático)' }}</option>
            <option v-for="ciclo in ciclos" :key="ciclo.id_ciclo" :value="String(ciclo.id_ciclo)">
              {{ ciclo.anio }} · {{ ciclo.estado }}
            </option>
          </select>
        </label>

        <label v-if="tipoReporte === 'cumplimiento'">
          Solicitud
          <select v-model="solicitudFiltro" @change="reiniciarResultado">
            <option value="">Todas las solicitudes</option>
            <option v-for="s in solicitudesCatalogo" :key="s.id_solicitud" :value="String(s.id_solicitud)">{{ s.titulo }}</option>
          </select>
        </label>
        <label v-else-if="tipoReporte === 'inventario'">
          Documento o responsable
          <input v-model="busquedaInventario" type="search" placeholder="Buscar por archivo, solicitud o docente" />
        </label>
        <label v-else>
          Grado o sección
          <select v-model="seccionSeleccionada" :disabled="!seccionesDisponibles.length">
            <option value="">Todos los grados</option>
            <option v-for="seccion in seccionesDisponibles" :key="seccion.id_seccion" :value="String(seccion.id_seccion)">{{ seccion.etiqueta }}</option>
          </select>
        </label>

        <label>
          Estado
          <select v-model="estadoSeleccionado" @change="reiniciarResultado" :disabled="tipoReporte === 'matriculas'">
            <option value="">Todos</option>
            <template v-if="tipoReporte === 'cumplimiento'">
              <option value="pendiente">Pendiente</option>
              <option value="vencido">Vencido</option>
              <option value="entregado">Con entrega registrada</option>
            </template>
            <template v-else-if="tipoReporte === 'inventario'">
              <option value="entregado">Entregado</option>
              <option value="en_revision">En revisión</option>
              <option value="correccion_solicitada">Corrección solicitada</option>
              <option value="aprobado">Aprobado</option>
              <option value="rechazado">Rechazado</option>
            </template>
            <template v-else-if="tipoReporte === 'expedientes'">
              <option value="completo">Completo</option>
              <option value="incompleto">Incompleto</option>
            </template>
          </select>
        </label>
      </div>

      <div class="reports-actions">
        <button type="button" @click="generarVistaPrevia" :disabled="cargando">
          {{ cargando ? 'Consultando...' : 'Generar vista previa' }}
        </button>
        <span v-if="errorCatalogos" class="reports-hint" role="status">{{ errorCatalogos }}</span>
      </div>
      <p v-if="error" class="error-message" role="alert">{{ error }}</p>
    </div>

    <div v-if="vistaPreviaGenerada && tipoReporte === 'inventario'" class="reports-card reports-result institutional-report">
      <div class="report-document-heading">
        <img :src="logoEscuela" alt="Escudo de la escuela" class="report-school-logo" />
        <div>
          <h2>Inventario documental</h2>
          <p>EORM Orfelinda Osorio Lemus · {{ etiquetaCicloInventario }} · Generado {{ fechaGeneracion }}</p>
        </div>
      </div>
      <div class="report-document-rule"></div>
      <p class="report-record-count">{{ filasInventario.length }} {{ filasInventario.length === 1 ? 'documento encontrado.' : 'documentos encontrados.' }}</p>
      <div class="table-scroll">
        <table class="report-document-table">
          <thead><tr><th>Archivo</th><th>Solicitud</th><th>Responsable</th><th>Fecha de entrega</th><th>Estado</th><th>Versión</th><th>Código</th></tr></thead>
          <tbody>
            <tr v-for="fila in filasInventario" :key="fila.id_entrega">
              <td>{{ fila.archivo }}</td>
              <td>{{ fila.solicitud || 'Sin solicitud' }}</td>
              <td>{{ fila.docente || 'Sin nombre' }}</td>
              <td>{{ fila.fecha || 'Sin registrar' }}</td>
              <td>{{ etiquetaEstadoInventario(fila.estado) }}</td>
              <td>{{ fila.version ?? '—' }}</td>
              <td>{{ fila.codigo || '—' }}</td>
            </tr>
            <tr v-if="!filasInventario.length"><td colspan="7" class="empty-row">No hay documentos entregados con los filtros seleccionados.</td></tr>
          </tbody>
        </table>
      </div>
      <div class="report-document-actions no-print">
        <button type="button" class="button-secondary" @click="exportarCSV" :disabled="!filasInventario.length">Exportar CSV</button>
        <button type="button" @click="imprimirPDF">Imprimir / Guardar PDF</button>
      </div>
      <p class="reports-footnote no-print">Alcance: archivos de entregas docentes registrados en la bandeja de revisión. No incluye aún los archivos de expedientes estudiantiles ni el repositorio institucional.</p>
    </div>

    <div v-if="vistaPreviaGenerada && (tipoReporte === 'matriculas' || tipoReporte === 'expedientes')" class="reports-card reports-result institutional-report">
      <div class="report-document-heading">
        <img :src="logoEscuela" alt="Escudo de la escuela" class="report-school-logo" />
        <div>
          <h2>{{ tipoReporte === 'matriculas' ? 'Reporte de matrículas' : 'Reporte de estado de expedientes' }}</h2>
          <p>EORM Orfelinda Osorio Lemus · Ciclo {{ cicloConsultado?.anio ?? 'no identificado' }} · Generado {{ fechaGeneracion }}</p>
        </div>
      </div>
      <div class="report-document-rule"></div>
      <p class="report-record-count">{{ filasEscolares.length }} {{ filasEscolares.length === 1 ? 'registro encontrado.' : 'registros encontrados.' }}</p>
      <div class="table-scroll">
        <table v-if="tipoReporte === 'matriculas'" class="report-document-table">
          <thead><tr><th>Código</th><th>Estudiante</th><th>Sección</th><th>Docente</th><th>Estado</th></tr></thead>
          <tbody>
            <tr v-for="e in filasEscolares" :key="e.id_matricula">
              <td>{{ e.codigo || '—' }}</td>
              <td>{{ e.nombre }}</td>
              <td>{{ e.seccion || 'Sin sección' }}</td>
              <td>{{ docenteDeEstudiante(e) }}</td>
              <td>Activa</td>
            </tr>
            <tr v-if="!filasEscolares.length"><td colspan="5" class="empty-row">No hay matrículas activas para el ciclo y los filtros seleccionados.</td></tr>
          </tbody>
        </table>
        <table v-else class="report-document-table">
          <thead><tr><th>Código</th><th>Estudiante</th><th>Sección</th><th>Estado del expediente</th><th>Documentos</th></tr></thead>
          <tbody>
            <tr v-for="e in filasEscolares" :key="e.id_matricula">
              <td>{{ e.codigo || '—' }}</td><td>{{ e.nombre }}</td><td>{{ e.seccion || 'Sin sección' }}</td>
              <td>{{ e.expediente?.completo ? 'Completo' : 'Incompleto' }}</td>
              <td>{{ e.expediente?.entregados ?? 0 }} / {{ e.expediente?.total ?? 0 }}</td>
            </tr>
            <tr v-if="!filasEscolares.length"><td colspan="5" class="empty-row">No hay expedientes para el ciclo y los filtros seleccionados.</td></tr>
          </tbody>
        </table>
      </div>
      <div class="report-document-actions no-print">
        <button type="button" class="button-secondary" @click="exportarCSV" :disabled="!filasEscolares.length">Exportar CSV</button>
        <button type="button" @click="imprimirPDF">Imprimir / Guardar PDF</button>
      </div>
    </div>

    <div v-if="vistaPreviaGenerada && tipoReporte === 'cumplimiento'" class="reports-card reports-result institutional-report">
      <div class="report-document-heading">
        <img :src="logoEscuela" alt="Escudo de la escuela" class="report-school-logo" />
        <div>
          <h2>Cumplimiento de entregas</h2>
          <p>EORM Orfelinda Osorio Lemus · {{ etiquetaCicloCumplimiento }} · Generado {{ fechaGeneracion }}</p>
        </div>
      </div>
      <div class="report-document-rule"></div>
      <p class="report-record-count">{{ filasCumplimiento.length }} {{ filasCumplimiento.length === 1 ? 'registro encontrado.' : 'registros encontrados.' }}</p>
      <div class="table-scroll">
        <table class="report-document-table report-compliance-table">
          <thead><tr><th>Solicitud</th><th>Docente</th><th>Secciones</th><th>Fecha límite</th><th>Fecha entrega</th><th>Estado</th><th>Código / ID</th></tr></thead>
          <tbody>
            <tr v-for="fila in filasCumplimiento" :key="`${fila.id_solicitud}-${fila.id_destinatario}`">
              <td>{{ fila.titulo }}</td>
              <td>{{ fila.docente || 'Sin nombre' }}</td>
              <td>{{ fila.alcance || 'Sin sección' }}</td>
              <td>{{ formatearFecha(fila.fecha_limite) }}</td>
              <td>{{ fila.fecha ? formatearFechaHora(fila.fecha) : '—' }}</td>
              <td>{{ etiquetaEstadoEntrega(fila) }}</td>
              <td>{{ fila.id_entrega != null ? `ID ${fila.id_entrega}` : '—' }}</td>
            </tr>
            <tr v-if="!filasCumplimiento.length"><td colspan="7" class="empty-row">No hay docentes destinatarios con los filtros seleccionados.</td></tr>
          </tbody>
        </table>
      </div>
      <div class="report-document-actions no-print">
        <button type="button" class="button-secondary" @click="exportarCSV" :disabled="!filasCumplimiento.length">Exportar CSV</button>
        <button type="button" @click="imprimirPDF">Imprimir / Guardar PDF</button>
      </div>
      <p class="reports-footnote no-print">La sección figura como «Sin sección» mientras no esté vinculada en el backend. El identificador de entrega es interno, no un código institucional.</p>
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
import './reports.css';
import api from '../../services/api';
import logoEscuela from '../../assets/images/logo.jpeg';

const tipoReporte = ref('cumplimiento');
const cicloSeleccionado = ref('');
const estadoSeleccionado = ref('');
const seccionSeleccionada = ref('');
const secciones = ref([]);
const estudiantes = ref([]);
const cicloConsultado = ref(null);
const fechaGeneracion = ref('');
const busqueda = ref('');
const ciclos = ref([]);
const solicitudes = ref([]);
const solicitudesCatalogo = ref([]);
const solicitudFiltro = ref('');
const inventarioBase = ref([]);
const busquedaInventario = ref('');
const filasCumplimientoBase = ref([]);
const vistaPreviaGenerada = ref(false);
const cargando = ref(false);
const error = ref('');
const errorCatalogos = ref('');
const solicitudSeleccionada = ref(null);
const detalle = ref([]);
const cargandoDetalle = ref(false);
const errorDetalle = ref('');

const etiquetas = {
  matriculas: 'Matrículas por grado',
  expedientes: 'Estado de expedientes',
  inventario: 'Inventario documental',
  cumplimiento: 'Cumplimiento de entregas'
};
const nombreReporte = computed(() => etiquetas[tipoReporte.value] || 'Reporte');
// La bandeja de revisión no devuelve id_ciclo, por eso vinculamos cada
// entrega con el código SOL-0001 y con las solicitudes consultadas en Flask.
function idSolicitudDeCodigo(codigo) {
  const match = String(codigo || '').match(/^SOL-(\d+)$/i);
  return match ? Number(match[1]) : null;
}
const etiquetaCicloInventario = computed(() => {
  if (!cicloSeleccionado.value) return 'Todos los ciclos';
  const ciclo = ciclos.value.find(c => String(c.id_ciclo) === cicloSeleccionado.value);
  return ciclo ? `Ciclo ${ciclo.anio}` : 'Ciclo seleccionado';
});
const filasInventario = computed(() => {
  const termino = busquedaInventario.value.trim().toLocaleLowerCase('es');
  const estado = estadoSeleccionado.value;
  return inventarioBase.value.filter(fila =>
    (!estado || String(fila.estado || '').toLowerCase() === estado) &&
    (!termino || [fila.archivo, fila.solicitud, fila.docente, fila.codigo]
      .some(campo => String(campo || '').toLocaleLowerCase('es').includes(termino)))
  );
});
function etiquetaEstadoInventario(estado) {
  const etiquetasEstado = {
    entregado: 'Entregado', en_revision: 'En revisión',
    correccion_solicitada: 'Corrección solicitada',
    aprobado: 'Aprobado', rechazado: 'Rechazado'
  };
  return etiquetasEstado[String(estado || '').toLowerCase()] || estado || 'Sin estado';
}

const seccionesDisponibles = computed(() => secciones.value);
const filasEscolares = computed(() => {
  const id = seccionSeleccionada.value;
  return estudiantes.value.filter(e =>
    (!id || String(e.id_seccion) === id) &&
    (tipoReporte.value !== 'expedientes' || !estadoSeleccionado.value ||
      (e.expediente?.completo ? 'completo' : 'incompleto') === estadoSeleccionado.value)
  );
});
function docenteDeEstudiante(estudiante) {
  const seccion = secciones.value.find(s => String(s.id_seccion) === String(estudiante.id_seccion));
  return seccion?.docente || 'Sin asignar';
}

const filasCumplimiento = computed(() => filasCumplimientoBase.value.filter(fila => {
  const filtro = estadoSeleccionado.value;
  if (!filtro) return true;
  if (filtro === 'entregado') return fila.id_entrega != null;
  return fila.estado?.toLowerCase() === filtro;
}));
const etiquetaCicloCumplimiento = computed(() => {
  if (!cicloSeleccionado.value) return 'Todos los ciclos';
  const ciclo = ciclos.value.find(c => String(c.id_ciclo) === cicloSeleccionado.value);
  return ciclo ? `Ciclo ${ciclo.anio}` : 'Ciclo seleccionado';
});
function etiquetaEstadoEntrega(fila) {
  return fila.estado || (fila.id_entrega != null ? 'Con entrega' : 'Pendiente');
}
function formatearFechaHora(valor) {
  if (!valor) return '—';
  const fecha = new Date(valor);
  if (Number.isNaN(fecha.getTime())) return 'Fecha no válida';
  return fecha.toLocaleString('es-GT', { timeZone: 'America/Guatemala', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

function formatearFecha(valor) {
  if (!valor) return 'Sin registrar';
  // YYYY-MM-DD: evitar el cambio de día por huso horario.
  if (typeof valor === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(valor)) {
    const [anio, mes, dia] = valor.split('-');
    return `${dia}/${mes}/${anio}`;
  }
  const fecha = new Date(valor);
  if (Number.isNaN(fecha.getTime())) return 'Fecha no válida';
  return fecha.toLocaleDateString('es-GT', { day: '2-digit', month: '2-digit', year: 'numeric', timeZone: 'America/Guatemala' });
}
function cerrarDetalle() {
  solicitudSeleccionada.value = null;
  detalle.value = [];
  errorDetalle.value = '';
}
function reiniciarVistaPrevia() {
  seccionSeleccionada.value = '';
  estadoSeleccionado.value = '';
  secciones.value = [];
  estudiantes.value = [];
  cicloConsultado.value = null;
  fechaGeneracion.value = '';
  vistaPreviaGenerada.value = false;
  error.value = '';
  busqueda.value = '';
  solicitudFiltro.value = '';
  filasCumplimientoBase.value = [];
  inventarioBase.value = [];
  busquedaInventario.value = '';
  cerrarDetalle();
}
function reiniciarResultado() {
  vistaPreviaGenerada.value = false;
  error.value = '';
}
function mensajeError(err, valorPorDefecto) {
  if (err.response?.status === 401) return 'La sesión expiró o no es válida. Cierre sesión y vuelva a iniciar.';
  if (err.response?.status === 403) return 'Su cuenta no tiene permiso para consultar este reporte.';
  return err.response?.data?.mensaje || err.response?.data?.error || valorPorDefecto;
}
async function generarVistaPrevia() {
  error.value = '';
  cerrarDetalle();
  vistaPreviaGenerada.value = false;
  cargando.value = true;
  try {
    if (tipoReporte.value === 'inventario') {
      const [entregasResponse, solicitudesResponse] = await Promise.all([
        api.get('/directora/revision'),
        obtenerSolicitudes(cicloSeleccionado.value ? Number(cicloSeleccionado.value) : null)
      ]);
      const entregas = entregasResponse.data?.entregas;
      const solicitudesInventario = solicitudesResponse?.solicitudes;
      if (!Array.isArray(entregas) || !Array.isArray(solicitudesInventario)) {
        throw new Error('Respuesta inesperada de inventario o solicitudes');
      }
      const idsPermitidos = new Set(solicitudesInventario.map(s => Number(s.id_solicitud)));
      inventarioBase.value = entregas.filter(e =>
        // Solo los archivos existentes y vinculados a una solicitud del ciclo filtrado.
        e.archivo && idsPermitidos.has(idSolicitudDeCodigo(e.codigo))
      );
    } else if (tipoReporte.value === 'cumplimiento') {
      const resultado = await obtenerSolicitudes(cicloSeleccionado.value ? Number(cicloSeleccionado.value) : null);
      if (!Array.isArray(resultado.solicitudes)) throw new Error('Respuesta de solicitudes inesperada');
      solicitudes.value = resultado.solicitudes;
      solicitudesCatalogo.value = resultado.solicitudes;
      const elegidas = resultado.solicitudes.filter(s => !solicitudFiltro.value || String(s.id_solicitud) === solicitudFiltro.value);
      // Una solicitud devuelve destinatarios individuales en /cumplimiento.
      const respuestas = await Promise.all(elegidas.map(async s => {
        const data = await obtenerCumplimiento(s.id_solicitud);
        if (!Array.isArray(data.cumplimiento)) throw new Error('Formato de cumplimiento inesperado');
        return data.cumplimiento.map(d => ({ ...d, id_solicitud: s.id_solicitud, titulo: s.titulo, fecha_limite: s.fecha_limite }));
      }));
      filasCumplimientoBase.value = respuestas.flat();
    } else {
      // La ruta sigue el patrón de requestsService.js; confirmar si el equipo cambió el prefijo.
      const resultado = await api.get('/directora/expedientes', {
        params: cicloSeleccionado.value ? { id_ciclo: Number(cicloSeleccionado.value) } : {}
      });
      if (!Array.isArray(resultado.data.estudiantes) || !Array.isArray(resultado.data.secciones)) {
        throw new Error('Respuesta de expedientes inesperada');
      }
      estudiantes.value = resultado.data.estudiantes;
      secciones.value = resultado.data.secciones;
      cicloConsultado.value = resultado.data.ciclo || null;
    }
    fechaGeneracion.value = new Date().toLocaleString('es-GT', { timeZone: 'America/Guatemala', dateStyle: 'short', timeStyle: 'short' });
    vistaPreviaGenerada.value = true;
  } catch (err) {
    error.value = mensajeError(err, `No se pudo cargar el reporte de ${nombreReporte.value.toLowerCase()}. Revise Flask y las rutas de la API.`);
  } finally {
    cargando.value = false;
  }
}

async function verDetalle(solicitud) {
  solicitudSeleccionada.value = solicitud;
  detalle.value = [];
  errorDetalle.value = '';
  cargandoDetalle.value = true;
  try {
    const resultado = await obtenerCumplimiento(solicitud.id_solicitud);
    if (solicitudSeleccionada.value?.id_solicitud === solicitud.id_solicitud) {
      detalle.value = Array.isArray(resultado.cumplimiento) ? resultado.cumplimiento : [];
    }
  } catch (err) {
    errorDetalle.value = mensajeError(err, 'No fue posible consultar el detalle de cumplimiento.');
  } finally {
    cargandoDetalle.value = false;
  }
}
function campoCSV(valor) {
  // Evita interpretar valores recibidos de la BD como fórmulas al abrir CSV en Excel.
  let texto = String(valor ?? '');
  if (/^[\s]*[=+@\-\t\r]/.test(texto)) texto = "'" + texto;
  return '"' + texto.replace(/"/g, '""') + '"';
}
function exportarCSV() {
  let filas;
  let nombreArchivo;
  if (tipoReporte.value === 'cumplimiento') {
    if (!filasCumplimiento.value.length) return;
    filas = [
      ['Solicitud', 'Docente', 'Secciones', 'Fecha límite', 'Fecha entrega', 'Estado', 'Código / ID'],
      ...filasCumplimiento.value.map(f => [f.titulo, f.docente, f.alcance || 'Sin sección', formatearFecha(f.fecha_limite), f.fecha ? formatearFechaHora(f.fecha) : '', etiquetaEstadoEntrega(f), f.id_entrega != null ? `ID ${f.id_entrega}` : ''])
    ];
    nombreArchivo = 'sgad-cumplimiento-entregas.csv';
  } else if (tipoReporte.value === 'matriculas') {
    if (!filasEscolares.value.length) return;
    filas = [
      ['Código', 'Estudiante', 'Sección', 'Docente', 'Estado'],
      ...filasEscolares.value.map(e => [e.codigo, e.nombre, e.seccion, docenteDeEstudiante(e), 'Activa'])
    ];
    nombreArchivo = 'sgad-matriculas-por-grado.csv';
  } else if (tipoReporte.value === 'expedientes') {
    if (!filasEscolares.value.length) return;
    filas = [
      ['Código', 'Estudiante', 'Grado y sección', 'Estado del expediente', 'Documentos entregados', 'Documentos requeridos'],
      ...filasEscolares.value.map(e => [e.codigo, e.nombre, e.seccion, e.expediente?.completo ? 'Completo' : 'Incompleto', e.expediente?.entregados ?? 0, e.expediente?.total ?? 0])
    ];
    nombreArchivo = 'sgad-estado-expedientes.csv';
  } else if (tipoReporte.value === 'inventario') {
    if (!filasInventario.value.length) return;
    filas = [
      ['Archivo', 'Solicitud', 'Responsable', 'Fecha entrega', 'Estado', 'Versión', 'Código solicitud'],
      ...filasInventario.value.map(f => [f.archivo, f.solicitud, f.docente, f.fecha, etiquetaEstadoInventario(f.estado), f.version, f.codigo])
    ];
    nombreArchivo = 'sgad-inventario-entregas-docentes.csv';
  } else return;
  const contenido = '\uFEFFsep=;\r\n' + filas.map(fila => fila.map(campoCSV).join(';')).join('\r\n');
  const url = URL.createObjectURL(new Blob([contenido], { type: 'text/csv;charset=utf-8;' }));
  const enlace = document.createElement('a');
  enlace.href = url;
  enlace.download = nombreArchivo;
  document.body.appendChild(enlace);
  enlace.click();
  enlace.remove();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

function imprimirPDF() {
  window.print(); // En el navegador elegir «Guardar como PDF».
}

onMounted(async () => {
  try {
    const resultado = await obtenerCatalogosSolicitudes();
    ciclos.value = Array.isArray(resultado.ciclos) ? resultado.ciclos : [];
  } catch (err) {
    errorCatalogos.value = mensajeError(err, 'No se pudo cargar el catálogo de ciclos.');
  }
});
</script>
