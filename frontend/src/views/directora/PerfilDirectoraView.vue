<template>
  <div class="director-layout">
    <DirectorSidebar />

    <div class="director-main">
      <DirectorTopbar />

      <main class="director-content perfil-area">
        <div class="perfil-contenedor">
          <header class="perfil-encabezado">
            <span>MI ESPACIO PERSONAL</span>
            <h1>Mi perfil</h1>
            <p>Información de mi cuenta institucional.</p>
          </header>

          <section class="perfil-tarjeta">
            <p v-if="cargando" class="perfil-aviso">
              Cargando información del perfil...
            </p>

            <p v-if="errorCarga" class="perfil-error">
              {{ errorCarga }}
            </p>

            <template v-if="perfil">
              <div class="perfil-identidad">
                <div class="perfil-avatar">
                  <img
                    v-if="fotoUrl"
                    :src="fotoUrl"
                    alt="Fotografía de perfil"
                  />
                  <span v-else>{{ iniciales }}</span>
                </div>

                <div class="perfil-identidad-datos">
                  <h2>{{ perfil.nombre_completo }}</h2>
                  <p>
                    {{ perfil.rol }} ·
                    Cuenta {{ perfil.activo ? "activa" : "inactiva" }}
                  </p>
                </div>

                <div class="perfil-foto-acciones">
                  <input
                    ref="entradaFoto"
                    type="file"
                    accept=".png,.jpg,.jpeg,.webp"
                    hidden
                    @change="seleccionarFoto"
                  />

                  <button
                    type="button"
                    class="perfil-boton-claro"
                    :disabled="guardandoFoto"
                    @click="$refs.entradaFoto.click()"
                  >
                    📷 Cambiar foto
                  </button>

                  <button
                    v-if="perfil.foto_disponible"
                    type="button"
                    class="perfil-boton-claro"
                    :disabled="guardandoFoto"
                    @click="eliminarFoto"
                  >
                    Quitar foto
                  </button>
                </div>
              </div>

              <div class="perfil-datos-grid">
                <article class="perfil-dato correo">
                  <span class="dato-icono">✉</span>
                  <span class="dato-etiqueta">
                    Correo institucional
                  </span>
                  <strong>{{ perfil.correo }}</strong>
                </article>

                <article class="perfil-dato telefono">
                  <span class="dato-icono">☎</span>
                  <span class="dato-etiqueta">Teléfono</span>
                  <strong>
                    {{ perfil.telefono || "No registrado" }}
                  </strong>
                </article>

                <article class="perfil-dato nacimiento">
                  <span class="dato-icono">▦</span>
                  <span class="dato-etiqueta">
                    Fecha de nacimiento
                  </span>
                  <strong>
                    {{ fechaVisible }}
                  </strong>
                </article>

                <article class="perfil-dato rol">
                  <span class="dato-icono">♙</span>
                  <span class="dato-etiqueta">
                    Rol institucional
                  </span>
                  <strong>{{ perfil.rol }}</strong>
                </article>
              </div>

              <div class="perfil-informacion-grid">
                <article class="perfil-informacion">
                  <h3>Mis secciones asignadas</h3>
                  <p class="perfil-texto-suave">
                    {{ cicloVisible }}
                  </p>
                  <p>Acceso institucional como Directora.</p>
                </article>

                <article class="perfil-informacion">
                  <h3>Seguridad de la cuenta</h3>
                  <p>
                    Tu cuenta es de uso individual. Los permisos
                    y asignaciones los administra Dirección.
                  </p>
                  <p class="perfil-texto-suave">
                    Google Authenticator protege el acceso a tu cuenta.
                    Si pierdes los códigos de recuperación, puedes generar
                    ocho nuevos verificando tu identidad.
                  </p>
                  <button
                    type="button"
                    class="perfil-boton-claro"
                    @click="abrirSeguridad"
                  >
                    Regenerar códigos de recuperación
                  </button>
                </article>
              </div>

              <div class="perfil-botones-finales">
                <button
                  type="button"
                  class="perfil-boton-claro"
                  @click="volverAlPanel"
                >
                  Volver al panel
                </button>

                <button
                  type="button"
                  class="perfil-boton-azul"
                  @click="abrirEditor"
                >
                  Editar perfil
                </button>
              </div>
            </template>
          </section>
        </div>
      </main>
    </div>

    <!-- VENTANA EDITAR PERFIL -->
    <div
      v-if="mostrarEditor"
      class="perfil-modal-fondo"
      @click.self="cerrarEditor"
    >
      <section
        class="perfil-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="titulo-editar-perfil"
      >
        <header class="perfil-modal-cabecera">
          <div>
            <span>DATOS PERSONALES</span>
            <h2 id="titulo-editar-perfil">
              Editar mi perfil
            </h2>
          </div>

          <button
            type="button"
            class="perfil-cerrar"
            aria-label="Cerrar"
            @click="cerrarEditor"
          >
            ×
          </button>
        </header>

        <form @submit.prevent="guardarPerfil">
          <div class="perfil-formulario">
            <label>
              Nombre completo <b>*</b>
              <input
                v-model.trim="formulario.nombre_completo"
                type="text"
                maxlength="201"
                required
              />
            </label>

            <label>
              Correo institucional
              <input
                v-model.trim="formulario.correo"
                type="email"
                maxlength="150"
                required
              />
            </label>

            <label>
              Teléfono
              <input
                v-model.trim="formulario.telefono"
                type="tel"
                maxlength="20"
                placeholder="Ej. 55555555"
              />
            </label>

            <label>
              Fecha de nacimiento (opcional)
              <input
                v-model="formulario.fecha_nacimiento"
                type="date"
                :max="fechaMaxima"
              />
            </label>

            <p v-if="errorFormulario" class="perfil-error">
              {{ errorFormulario }}
            </p>
          </div>

          <footer class="perfil-modal-pie">
            <button
              type="button"
              class="perfil-boton-claro"
              :disabled="guardando"
              @click="cerrarEditor"
            >
              Cancelar
            </button>

            <button
              type="submit"
              class="perfil-boton-azul"
              :disabled="guardando"
            >
              {{ guardando ? "Guardando..." : "Guardar cambios" }}
            </button>
          </footer>
        </form>
      </section>
    </div>

    <!-- REGENERACIÓN DE CÓDIGOS DE RECUPERACIÓN 2FA -->
    <div
      v-if="mostrarSeguridad"
      class="perfil-modal-fondo"
      @click.self="cerrarSeguridad"
    >
      <section
        class="perfil-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="titulo-seguridad"
      >
        <header class="perfil-modal-cabecera">
          <div>
            <span>SEGURIDAD DE LA CUENTA</span>
            <h2 id="titulo-seguridad">Códigos de recuperación</h2>
          </div>
          <button
            type="button"
            class="perfil-cerrar"
            aria-label="Cerrar"
            :disabled="regenerandoCodigos"
            @click="cerrarSeguridad"
          >×</button>
        </header>

        <form
          v-if="codigosNuevos.length === 0"
          @submit.prevent="regenerarCodigos"
        >
          <div class="perfil-formulario">
            <p>
              Se crearán 8 códigos nuevos y todos los anteriores
              dejarán de funcionar. Guarda los nuevos en un lugar seguro.
            </p>
            <label>
              Código actual de Google Authenticator
              <input
                v-model.trim="codigoAuthenticator"
                type="text"
                inputmode="numeric"
                autocomplete="one-time-code"
                maxlength="6"
                pattern="[0-9]{6}"
                placeholder="6 dígitos"
                required
              />
            </label>
            <p v-if="errorSeguridad" class="perfil-error" role="alert">
              {{ errorSeguridad }}
            </p>
          </div>
          <footer class="perfil-modal-pie">
            <button
              type="button"
              class="perfil-boton-claro"
              :disabled="regenerandoCodigos"
              @click="cerrarSeguridad"
            >Cancelar</button>
            <button
              type="submit"
              class="perfil-boton-azul"
              :disabled="regenerandoCodigos || !/^[0-9]{6}$/.test(codigoAuthenticator)"
            >
              {{ regenerandoCodigos ? "Verificando..." : "Generar 8 códigos nuevos" }}
            </button>
          </footer>
        </form>

        <div v-else>
          <div class="perfil-formulario">
            <p><strong>Códigos generados correctamente.</strong></p>
            <p>
              Se muestran una sola vez. Los códigos anteriores ya no sirven.
              No los compartas ni tomes capturas de pantalla.
            </p>
            <div class="perfil-codigos-grid" aria-label="Nuevos códigos de recuperación">
              <code v-for="(item, indice) in codigosNuevos" :key="indice">
                {{ item }}
              </code>
            </div>
            <p v-if="errorSeguridad" class="perfil-error" role="alert">
              {{ errorSeguridad }}
            </p>
          </div>
          <footer class="perfil-modal-pie">
            <button type="button" class="perfil-boton-claro" @click="copiarCodigos">
              Copiar códigos
            </button>
            <button type="button" class="perfil-boton-azul" @click="cerrarSeguridad">
              Ya los guardé, cerrar
            </button>
          </footer>
        </div>
      </section>
    </div>

    <!-- MENSAJE DE CONFIRMACIÓN -->
    <div
      v-if="notificacion"
      class="perfil-notificacion"
      :class="{ fallo: notificacionError }"
      role="status"
    >
      <span>{{ notificacionError ? "!" : "✓" }}</span>
      <p>{{ notificacion }}</p>
      <button
        type="button"
        aria-label="Cerrar mensaje"
        @click="notificacion = ''"
      >
        ×
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import api from "../../services/api";

import DirectorSidebar from "../../components/layout/DirectorSidebar.vue";
import DirectorTopbar from "../../components/layout/DirectorTopbar.vue";

import {
  obtenerPerfilDirectora,
  actualizarPerfilDirectora,
  cambiarFotoPerfilDirectora,
  obtenerFotoPerfilDirectora,
  quitarFotoPerfilDirectora
} from "../../services/perfilDirectoraService";

import "../../assets/css/director.css";

const router = useRouter();

const perfil = ref(null);
const fotoUrl = ref("");
const entradaFoto = ref(null);

const cargando = ref(true);
const guardando = ref(false);
const guardandoFoto = ref(false);

const mostrarEditor = ref(false);
const mostrarSeguridad = ref(false);
const codigoAuthenticator = ref("");
const codigosNuevos = ref([]);
const errorSeguridad = ref("");
const regenerandoCodigos = ref(false);
const errorCarga = ref("");
const errorFormulario = ref("");

const notificacion = ref("");
const notificacionError = ref(false);

const formulario = ref({
  nombre_completo: "",
  correo: "",
  telefono: "",
  fecha_nacimiento: ""
});

const fechaMaxima = new Date().toLocaleDateString(
  "en-CA"
);

const iniciales = computed(() => {
  if (!perfil.value) return "";

  const nombre = perfil.value.nombres?.charAt(0) || "";
  const apellido = perfil.value.apellidos?.charAt(0) || "";

  return `${nombre}${apellido}`.toUpperCase();
});

const fechaVisible = computed(() => {
  const fecha = perfil.value?.fecha_nacimiento;
  if (!fecha) return "No registrada";

  const partes = fecha.split("-");
  if (partes.length !== 3) return fecha;

  return `${partes[2]}/${partes[1]}/${partes[0]}`;
});

const cicloVisible = computed(() => {
  // La barra de ciclo escolar será integrada por el equipo.
  return "Ciclo escolar";
});


let temporizadorNotificacion = null;

function avisar(mensaje, esError = false) {
  // Cancelar el temporizador de un mensaje anterior.
  if (temporizadorNotificacion) {
    clearTimeout(temporizadorNotificacion);
  }

  notificacion.value = mensaje;
  notificacionError.value = esError;

  // Desaparecer automáticamente después de 3 segundos.
  temporizadorNotificacion = setTimeout(() => {
    notificacion.value = "";
    temporizadorNotificacion = null;
  }, 4000);
}


function obtenerError(error, alternativo) {
  return (
    error?.response?.data?.mensaje ||
    error?.response?.data?.message ||
    alternativo
  );
}

function actualizarUsuarioLocal() {
  const usuarioAnterior = JSON.parse(
    localStorage.getItem("usuario") || "{}"
  );

  localStorage.setItem(
    "usuario",
    JSON.stringify({
      ...usuarioAnterior,
      nombres: perfil.value.nombres,
      apellidos: perfil.value.apellidos,
      correo: perfil.value.correo,
      rol: perfil.value.rol
    })
  );

  window.dispatchEvent(new Event("sgad-perfil-actualizado"));
}

async function cargarFoto() {
  if (fotoUrl.value) {
    URL.revokeObjectURL(fotoUrl.value);
    fotoUrl.value = "";
  }

  if (!perfil.value?.foto_disponible) return;

  try {
    const archivo = await obtenerFotoPerfilDirectora();
    fotoUrl.value = URL.createObjectURL(archivo);
  } catch {
    fotoUrl.value = "";
  }
}

async function cargarPerfil() {
  cargando.value = true;
  errorCarga.value = "";

  try {
    const respuesta = await obtenerPerfilDirectora();
    perfil.value = respuesta.perfil;
    await cargarFoto();
  } catch (error) {
    errorCarga.value = obtenerError(
      error,
      "No fue posible cargar la información del perfil."
    );
  } finally {
    cargando.value = false;
  }
}

function abrirEditor() {
  if (!perfil.value) return;

  formulario.value = {
    nombre_completo: perfil.value.nombre_completo || "",
    correo: perfil.value.correo || "",
    telefono: perfil.value.telefono || "",
    fecha_nacimiento: perfil.value.fecha_nacimiento || ""
  };

  errorFormulario.value = "";
  mostrarEditor.value = true;
}

function cerrarEditor() {
  if (guardando.value) return;
  mostrarEditor.value = false;
  errorFormulario.value = "";
}

async function guardarPerfil() {
  const nombreCompleto = formulario.value.nombre_completo
    .trim()
    .replace(/\s+/g, " ");

  const palabras = nombreCompleto.split(" ").filter(Boolean);

  if (palabras.length < 2) {
    errorFormulario.value =
      "Ingrese por lo menos un nombre y un apellido.";
    return;
  }

  /*
    El prototipo utiliza un único campo de nombre completo.
    Conservamos la cantidad actual de palabras del campo
    nombres para separar nombres y apellidos.
  */
  const cantidadNombres = Math.min(
    (perfil.value.nombres || "").trim().split(/\s+/).length,
    palabras.length - 1
  );

  const nombres = palabras.slice(0, cantidadNombres).join(" ");
  const apellidos = palabras.slice(cantidadNombres).join(" ");

  guardando.value = true;
  errorFormulario.value = "";

  try {
    const respuesta = await actualizarPerfilDirectora({
      nombres,
      apellidos,
      correo: formulario.value.correo,
      telefono: formulario.value.telefono,
      fecha_nacimiento: formulario.value.fecha_nacimiento || null
    });

    perfil.value = respuesta.perfil;
    actualizarUsuarioLocal();

    mostrarEditor.value = false;
    avisar(
      respuesta.mensaje || "Perfil actualizado correctamente."
    );
  } catch (error) {
    errorFormulario.value = obtenerError(
      error,
      "No fue posible guardar los cambios."
    );
  } finally {
    guardando.value = false;
  }
}

async function seleccionarFoto(evento) {
  const archivo = evento.target.files?.[0];
  if (!archivo) return;

  if (
    !["image/png", "image/jpeg", "image/webp"].includes(
      archivo.type
    )
  ) {
    avisar("Seleccione una imagen PNG, JPG, JPEG o WEBP.", true);
    evento.target.value = "";
    return;
  }

  if (archivo.size > 5 * 1024 * 1024) {
    avisar("La fotografía no puede superar 5 MB.", true);
    evento.target.value = "";
    return;
  }

  guardandoFoto.value = true;

  try {
    const respuesta = await cambiarFotoPerfilDirectora(archivo);
    perfil.value = respuesta.perfil;
    await cargarFoto();

    window.dispatchEvent(new Event("sgad-perfil-actualizado"));

    avisar(
      respuesta.mensaje ||
      "Foto de perfil actualizada correctamente."
    );
  } catch (error) {
    avisar(
      obtenerError(error, "No fue posible cambiar la fotografía."),
      true
    );
  } finally {
    guardandoFoto.value = false;
    evento.target.value = "";
  }
}

async function eliminarFoto() {
  guardandoFoto.value = true;

  try {
    const respuesta = await quitarFotoPerfilDirectora();
    perfil.value = respuesta.perfil;
    await cargarFoto();

    window.dispatchEvent(new Event("sgad-perfil-actualizado"));

    avisar(
      respuesta.mensaje ||
      "Fotografía eliminada. Se muestran las iniciales."
    );
  } catch (error) {
    avisar(
      obtenerError(error, "No fue posible quitar la fotografía."),
      true
    );
  } finally {
    guardandoFoto.value = false;
  }
}

function abrirSeguridad() {
  codigoAuthenticator.value = "";
  codigosNuevos.value = [];
  errorSeguridad.value = "";
  mostrarSeguridad.value = true;
}

function cerrarSeguridad() {
  if (regenerandoCodigos.value) return;
  mostrarSeguridad.value = false;
  codigoAuthenticator.value = "";
  codigosNuevos.value = [];
  errorSeguridad.value = "";
}

async function regenerarCodigos() {
  if (regenerandoCodigos.value || !/^[0-9]{6}$/.test(codigoAuthenticator.value)) return;
  errorSeguridad.value = "";
  regenerandoCodigos.value = true;

  try {
    const respuesta = await api.post(
      "/auth/2fa/recovery-codes/regenerate",
      { codigo: codigoAuthenticator.value }
    );
    const codigos = respuesta.data?.codigos_recuperacion;
    if (!Array.isArray(codigos) || codigos.length !== 8) {
      throw new Error("El servidor no devolvió los 8 códigos esperados.");
    }
    codigosNuevos.value = codigos;
    codigoAuthenticator.value = "";
  } catch (error) {
    errorSeguridad.value = obtenerError(
      error,
      error.message || "No fue posible regenerar los códigos."
    );
  } finally {
    regenerandoCodigos.value = false;
  }
}

async function copiarCodigos() {
  try {
    await navigator.clipboard.writeText(codigosNuevos.value.join("\n"));
    avisar("Códigos copiados. Guárdalos en un lugar seguro.");
  } catch {
    errorSeguridad.value = "No se pudieron copiar. Guarda los códigos manualmente.";
  }
}

function volverAlPanel() {
  router.push("/directora/dashboard");
}

onMounted(cargarPerfil);

onUnmounted(() => {
  if (temporizadorNotificacion) {
    clearTimeout(temporizadorNotificacion);
  }

  if (fotoUrl.value) {
    URL.revokeObjectURL(fotoUrl.value);
  }
});
</script>

<style scoped>
.perfil-area {
  padding: 18px 26px 24px;
}

.perfil-contenedor {
  width: 100%;
  max-width: 1010px;
  margin: 0 auto;
}

.perfil-encabezado {
  margin-bottom: 13px;
}

.perfil-encabezado span,
.perfil-modal-cabecera span {
  color: #0879a7;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 1.5px;
}

.perfil-encabezado h1 {
  margin: 4px 0;
  color: #11466c;
  font-size: 27px;
}

.perfil-encabezado p {
  margin: 0;
  color: #69849c;
  font-size: 14px;
}

.perfil-tarjeta {
  padding: 20px 24px;
  background: white;
  border: 1px solid #d8e8f3;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(17, 70, 108, .05);
}

.perfil-identidad {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 15px;
  margin-bottom: 15px;
  border-bottom: 1px solid #dce7ef;
}

.perfil-avatar {
  width: 65px;
  height: 65px;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  border-radius: 17px;
  background: #11466c;
  color: white;
  font-size: 25px;
  font-weight: 800;
  overflow: hidden;
}

.perfil-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.perfil-identidad-datos {
  flex: 1;
  min-width: 0;
}

.perfil-identidad-datos h2 {
  margin: 0 0 5px;
  color: #11466c;
  font-size: 21px;
}

.perfil-identidad-datos p {
  margin: 0;
  color: #6885a3;
  font-size: 14px;
}

.perfil-foto-acciones {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.perfil-datos-grid,
.perfil-informacion-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}

.perfil-dato {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 15px 19px;
  border-radius: 15px;
  min-width: 0;
  font-size: 14px;
}

.dato-icono {
  font-size: 20px;
  margin-bottom: 2px;
}

.dato-etiqueta {
  font-weight: 700;
}

.perfil-dato strong {
  font-size: 15px;
  overflow-wrap: anywhere;
}

.correo {
  background: #e4f3df;
  color: #176c32;
}

.telefono {
  background: #fff0c6;
  color: #855300;
}

.nacimiento {
  background: #ddf3fb;
  color: #00618b;
}

.rol {
  background: #fde6e5;
  color: #ad393e;
}

.perfil-informacion {
  padding: 17px 19px;
  border: 1px solid #d6e5ef;
  border-radius: 15px;
  background: #f8fbfd;
  min-height: 126px;
}

.perfil-informacion h3 {
  margin: 0 0 12px;
  color: #11466c;
  font-size: 16px;
}

.perfil-informacion p {
  font-size: 13px;
  line-height: 1.5;
  margin: 0 0 9px;
  color: #173c58;
}

.perfil-informacion .perfil-texto-suave {
  color: #6885a3;
}

.perfil-botones-finales {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 14px;
}

.perfil-boton-claro,
.perfil-boton-azul {
  padding: 11px 17px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 750;
  cursor: pointer;
  transition: .15s ease;
}

.perfil-boton-claro {
  color: #11466c;
  background: white;
  border: 1px solid #bfd8e9;
}

.perfil-boton-azul {
  color: white;
  background: #11466c;
  border: 1px solid #11466c;
}

.perfil-boton-claro:hover {
  background: #eff8fd;
}

.perfil-boton-azul:hover {
  background: #0b3655;
}

button:disabled {
  opacity: .6;
  cursor: not-allowed;
}

.perfil-aviso {
  color: #647e95;
}

.perfil-error {
  color: #b42332;
  font-size: 13px;
  font-weight: 600;
}

/* FORMULARIO EMERGENTE */
.perfil-modal-fondo {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background: rgba(9, 33, 51, .66);
}

.perfil-modal {
  width: min(100%, 760px);
  max-height: calc(100vh - 32px);
  overflow-y: auto;
  border-radius: 22px;
  background: white;
  box-shadow: 0 20px 65px rgba(0, 0, 0, .24);
}

.perfil-modal-cabecera {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 22px 27px 18px;
  border-bottom: 1px solid #dae6ed;
}

.perfil-modal-cabecera h2 {
  margin: 6px 0 0;
  color: #11466c;
  font-size: 27px;
}

.perfil-cerrar {
  border: 0;
  background: none;
  color: #658198;
  font-size: 28px;
  cursor: pointer;
}

.perfil-formulario {
  padding: 20px 27px;
  display: grid;
  gap: 15px;
}

.perfil-formulario label {
  display: grid;
  gap: 8px;
  color: #173c58;
  font-size: 14px;
  font-weight: 750;
}

.perfil-formulario label b {
  color: #c33737;
}

.perfil-formulario input {
  width: 100%;
  min-height: 47px;
  padding: 10px 14px;
  border: 1px solid #c8dbea;
  border-radius: 12px;
  background: white;
  color: #153c5a;
  font: inherit;
  font-weight: 400;
}

.perfil-formulario input:focus {
  outline: 2px solid #b9e4f7;
  border-color: #158ac0;
}

.perfil-modal-pie {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 27px;
  background: #fafcfd;
  border-top: 1px solid #dae6ed;
}

/* MENSAJES */
.perfil-notificacion {
  position: fixed;
  z-index: 3000;
  right: 22px;
  bottom: 22px;
  width: min(450px, calc(100vw - 44px));
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 17px 20px;
  border-radius: 15px;
  background: #126a56;
  color: white;
  box-shadow: 0 10px 26px rgba(0, 0, 0, .16);
}

.perfil-notificacion.fallo {
  background: #b43e45;
}

.perfil-notificacion span {
  font-size: 22px;
  font-weight: 800;
}

.perfil-notificacion p {
  margin: 0;
  flex: 1;
  font-size: 14px;
}

.perfil-notificacion button {
  background: transparent;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
}

.perfil-codigos-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 9px;
}

.perfil-codigos-grid code {
  padding: 12px;
  border: 1px solid #d6e5ef;
  border-radius: 10px;
  background: #f3f8fc;
  color: #11466c;
  text-align: center;
  font-size: 14px;
  overflow-wrap: anywhere;
}

@media (max-width: 760px) {
  .perfil-area {
    padding: 14px;
  }

  .perfil-tarjeta {
    padding: 16px;
  }

  .perfil-identidad {
    flex-wrap: wrap;
  }

  .perfil-foto-acciones {
    width: 100%;
    justify-content: flex-start;
  }

  .perfil-datos-grid,
  .perfil-informacion-grid {
    grid-template-columns: 1fr;
  }

  .perfil-botones-finales {
    flex-wrap: wrap;
  }

  .perfil-codigos-grid {
    grid-template-columns: 1fr;
  }

  .perfil-modal-cabecera,
  .perfil-formulario,
  .perfil-modal-pie {
    padding-left: 17px;
    padding-right: 17px;
  }
}
</style>
