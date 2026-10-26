
<template>
  <section class="reports-page">
    <header class="reports-header">
      <p class="reports-eyebrow">GESTIÓN DOCUMENTAL</p>
      <h1>Reportes</h1>
      <p>
        Consulte el cumplimiento de las solicitudes documentales
        utilizando los registros del SGAD.
      </p>
    </header>

    <div class="reports-card">
      <div class="section-heading">
        <div>
          <h2>Cumplimiento documental</h2>
          <p>Seguimiento de entregas solicitadas a los docentes.</p>
        </div>
        <button @click="cargarDatos" :disabled="cargando">
          Actualizar
        </button>
      </div>

      <div class="filters">
        <label>
          Ciclo escolar
          <select v-model="cicloSeleccionado" @change="cargarDatos">
            <option value="">Todos los ciclos</option>
            <option
              v-for="ciclo in ciclos"
              :key="ciclo.id_ciclo"
              :value="String(ciclo.id_ciclo)"
            >
              {{ ciclo.anio }} · {{ ciclo.estado }}
            </option>
          </select>
        </label>

        <label>
          Buscar solicitud
          <input
            v-model="busqueda"
            placeholder="Escriba el nombre del documento"
          />
        </label>
      </div>

      <p v-if="cargando" class="info-message">
        Cargando información...
      </p>

      <p v-if="error" class="error-message" role="alert">
        {{ error }}
      </p>

      <template v-if="!cargando && !error">
        <div class="stats">
          <div class="stat-card">
            <span>Solicitudes</span>
            <strong>{{ solicitudesFiltradas.length }}</strong>
          </div>
          <div class="stat-card">
            <span>Entregas esperadas</span>
            <strong>{{ totalEsperadas }}</strong>
          </div>
          <div class="stat-card">
            <span>Entregas realizadas</span>
            <strong>{{ totalRealizadas }}</strong>
          </div>
          <div class="stat-card">
            <span>Cumplimiento</span>
            <strong>{{ porcentajeGeneral }}%</strong>
          </div>
        </div>

        <div class="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Solicitud</th>
                <th>Fecha límite</th>
                <th>Estado</th>
                <th>Entregas</th>
                <th>Cumplimiento</th>
                <th>Detalle</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="solicitud in solicitudesFiltradas"
                :key="solicitud.id_solicitud"
              >
                <td>{{ solicitud.titulo }}</td>
                <td>{{ formatearFecha(solicitud.fecha_limite) }}</td>
                <td>{{ solicitud.estado }}</td>
                <td>
                  {{ solicitud.total_entregados }} /
                  {{ solicitud.total_destinatarios }}
                </td>
                <td>
                  <div class="progress">
                    <div
                      class="progress-bar"
                      :style="{
                        width: `${solicitud.porcentaje_cumplimiento || 0}%`
                      }"
                    ></div>
                  </div>
                  {{ solicitud.porcentaje_cumplimiento || 0 }}%
                </td>
                <td>
                  <button
                    class="small-button"
                    @click="verDetalle(solicitud)"
                  >
                    Ver
                  </button>
                </td>
              </tr>

              <tr v-if="solicitudesFiltradas.length === 0">
                <td colspan="6" class="empty-row">
                  No se encontraron solicitudes con estos filtros.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>

    <div v-if="solicitudSeleccionada" class="reports-card detail-card">
      <div class="section-heading">
        <div>
          <h2>{{ solicitudSeleccionada.titulo }}</h2>
          <p>Detalle de cumplimiento por docente</p>
        </div>
        <button @click="cerrarDetalle">Cerrar detalle</button>
      </div>

      <p v-if="cargandoDetalle">Consultando entregas...</p>
      <p v-if="errorDetalle" class="error-message">
        {{ errorDetalle }}
      </p>

      <div v-if="!cargandoDetalle && !errorDetalle" class="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Docente</th>
              <th>Estado</th>
              <th>Fecha</th>
              <th>Archivo</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="fila in detalle"
              :key="fila.id_destinatario"
            >
              <td>{{ fila.docente }}</td>
              <td>{{ fila.estado }}</td>
              <td>{{ formatearFecha(fila.fecha) }}</td>
              <td>{{ fila.archivo || "Sin archivo" }}</td>
            </tr>
            <tr v-if="detalle.length === 0">
              <td colspan="4" class="empty-row">
                No hay docentes destinatarios registrados.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import {
  obtenerSolicitudes,
  obtenerCatalogosSolicitudes,
  obtenerCumplimiento
} from "../../services/requestsService";

const solicitudes = ref([]);
const ciclos = ref([]);
const busqueda = ref("");
const cicloSeleccionado = ref("");
const cargando = ref(false);
const error = ref("");

const solicitudSeleccionada = ref(null);
const detalle = ref([]);
const cargandoDetalle = ref(false);
const errorDetalle = ref("");

const solicitudesFiltradas = computed(() => {
  const texto = busqueda.value.trim().toLowerCase();

  return solicitudes.value.filter((solicitud) =>
    (solicitud.titulo || "").toLowerCase().includes(texto)
  );
});

const totalEsperadas = computed(() =>
  solicitudesFiltradas.value.reduce(
    (total, solicitud) =>
      total + Number(solicitud.total_destinatarios || 0),
    0
  )
);

const totalRealizadas = computed(() =>
  solicitudesFiltradas.value.reduce(
    (total, solicitud) =>
      total + Number(solicitud.total_entregados || 0),
    0
  )
);

const porcentajeGeneral = computed(() =>
  totalEsperadas.value
    ? Math.round(totalRealizadas.value * 100 / totalEsperadas.value)
    : 0
);

function formatearFecha(valor) {
  if (!valor) return "Sin registrar";

  const fecha = new Date(valor);
  return Number.isNaN(fecha.getTime())
    ? "Fecha no válida"
    : fecha.toLocaleDateString("es-GT", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        timeZone: "America/Guatemala"
      });
}

function cerrarDetalle() {
  solicitudSeleccionada.value = null;
  detalle.value = [];
  errorDetalle.value = "";
}

async function cargarDatos() {
  cargando.value = true;
  error.value = "";
  cerrarDetalle();

  try {
    const resultado = await obtenerSolicitudes(
      cicloSeleccionado.value
        ? Number(cicloSeleccionado.value)
        : null
    );
    solicitudes.value = resultado.solicitudes || [];
  } catch (err) {
    solicitudes.value = [];
    error.value =
      err.response?.data?.mensaje ||
      "No fue posible consultar las solicitudes.";
  } finally {
    cargando.value = false;
  }
}

async function verDetalle(solicitud) {
  solicitudSeleccionada.value = solicitud;
  detalle.value = [];
  errorDetalle.value = "";
  cargandoDetalle.value = true;

  try {
    const resultado = await obtenerCumplimiento(
      solicitud.id_solicitud
    );

    if (solicitudSeleccionada.value?.id_solicitud ===
        solicitud.id_solicitud) {
      detalle.value = resultado.cumplimiento || [];
    }
  } catch (err) {
    errorDetalle.value =
      err.response?.data?.mensaje ||
      "No fue posible consultar el cumplimiento.";
  } finally {
    cargandoDetalle.value = false;
  }
}

onMounted(async () => {
  try {
    const catalogos = await obtenerCatalogosSolicitudes();
    ciclos.value = catalogos.ciclos || [];
  } catch {
    // El reporte puede funcionar sin el catálogo de ciclos.
  }

  await cargarDatos();
});
</script>

<style scoped>
.reports-page {
  padding: 30px;
  min-height: 100%;
  background: #f1f7fa;
  color: #123e60;
}

.reports-eyebrow {
  color: #139dc2;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 2px;
}

.reports-header {
  margin-bottom: 24px;
}

.reports-header h1 {
  font-size: 36px;
  margin: 8px 0;
}

.reports-header p,
.section-heading p {
  color: #607b91;
}

.reports-card {
  background: white;
  border: 1px solid #dce9ef;
  border-radius: 18px;
  padding: 25px;
  margin-bottom: 22px;
}

.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 22px;
}

.section-heading h2 {
  margin: 0 0 8px;
}

button {
  background: #174d74;
  color: white;
  padding: 11px 17px;
  border: 0;
  border-radius: 9px;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: wait;
}

.filters {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
  margin-bottom: 24px;
}

.filters label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-weight: 600;
}

.filters select,
.filters input {
  padding: 12px;
  border: 1px solid #cbdce6;
  border-radius: 9px;
  background: white;
  color: #123e60;
  width: 100%;
  box-sizing: border-box;
}

.stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 24px;
}

.stat-card {
  padding: 18px;
  border-radius: 12px;
  background: #eaf6fb;
}

.stat-card span {
  display: block;
  font-size: 13px;
  margin-bottom: 8px;
}

.stat-card strong {
  font-size: 29px;
}

.table-scroll {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

th, td {
  text-align: left;
  padding: 13px;
  border-bottom: 1px solid #e4edf2;
}

th {
  background: #f2f7fa;
}

.progress {
  background: #e2edf1;
  height: 7px;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 5px;
}

.progress-bar {
  background: #24b4bd;
  height: 100%;
}

.small-button {
  padding: 8px 13px;
}

.empty-row {
  text-align: center;
  color: #607b91;
}

.error-message {
  background: #fff0ef;
  color: #a83232;
  padding: 13px;
  border-radius: 9px;
}

.info-message {
  color: #607b91;
}

@media (max-width: 850px) {
  .reports-page {
    padding: 16px;
  }

  .filters {
    grid-template-columns: 1fr;
  }

  .stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .section-heading {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
