<template>
  <div class="teacher-layout">
    <TeacherSidebar />

    <div class="teacher-main">
      <TeacherTopbar />

      <main class="profile-page">
        <header class="profile-heading">
          <p>
            MI ESPACIO PERSONAL
          </p>

          <h1>
            Mi perfil
          </h1>

          <span>
            Información de mi cuenta institucional.
          </span>
        </header>

        <div
          v-if="cargando"
          class="profile-message"
        >
          Cargando perfil...
        </div>

        <div
          v-else-if="error"
          class="profile-message"
        >
          {{ error }}
        </div>

        <section
          v-else-if="perfil"
          class="profile-card"
        >
          <div class="profile-main-row">
            <div class="profile-identity">
              <div class="profile-avatar">
                <img
                  v-if="fotoUrl"
                  :src="fotoUrl"
                  alt="Foto de perfil"
                />

                <span v-else>
                  {{ iniciales }}
                </span>
              </div>

              <div>
                <h2>
                  {{ perfil.nombre_completo }}
                </h2>

                <p>
                  Docente ·
                  {{
                    perfil.activo
                      ? "Cuenta activa"
                      : "Cuenta inactiva"
                  }}
                </p>
              </div>
            </div>

            <button
              type="button"
              class="profile-photo-button"
              @click="abrirSelectorFoto"
            >
              ▣ Cambiar foto
            </button>

            <input
              ref="fotoInput"
              type="file"
              accept=".png,.jpg,.jpeg,.webp"
              hidden
              @change="seleccionarFoto"
            />
          </div>

          <div class="profile-divider"></div>

          <div class="profile-info-grid">
            <article class="profile-info-card green">
              <span class="profile-info-icon">
                ✉
              </span>

              <small>
                Correo institucional
              </small>

              <strong>
                {{ perfil.correo }}
              </strong>
            </article>

            <article class="profile-info-card yellow">
              <span class="profile-info-icon">
                ☎
              </span>

              <small>
                Teléfono
              </small>

              <strong>
                {{
                  perfil.telefono
                  || "No registrado"
                }}
              </strong>
            </article>

            <article class="profile-info-card blue">
              <span class="profile-info-icon">
                ▦
              </span>

              <small>
                Fecha de nacimiento
              </small>

              <strong>
                {{
                  perfil.fecha_nacimiento
                    ? formatearFecha(
                        perfil.fecha_nacimiento
                      )
                    : "No registrada"
                }}
              </strong>
            </article>

            <article class="profile-info-card red">
              <span class="profile-info-icon">
                ♙
              </span>

              <small>
                Rol institucional
              </small>

              <strong>
                {{ perfil.rol }}
              </strong>
            </article>
          </div>

          <div class="profile-lower-grid">
            <article class="profile-lower-card">
              <h3>
                Mis secciones asignadas
              </h3>

              <p>
                Ciclo {{ anioCiclo }}
              </p>

              <div class="profile-section-line"></div>

              <div
                v-if="perfil.secciones?.length"
              >
                <div
                  v-for="seccion in perfil.secciones"
                  :key="seccion.id_seccion"
                  class="profile-section-item"
                >
                  <span>▮</span>

                  <strong>
                    {{ seccion.etiqueta }}
                  </strong>
                </div>
              </div>

              <span
                v-else
                class="profile-no-section"
              >
                Sin secciones asignadas.
              </span>
            </article>

            <article class="profile-lower-card">
              <h3>
                Seguridad de la cuenta
              </h3>

              <p class="profile-security-text">
                Tu cuenta es de uso individual.
                Los permisos y asignaciones los administra Dirección.
              </p>

              <p class="profile-security-note">
                El cambio de contraseña se habilitará
                cuando definamos el sistema de autenticación.
              </p>
            </article>
          </div>

          <div class="profile-actions">
            <button
              type="button"
              class="profile-back-button"
              @click="volverPanel"
            >
              Volver al panel
            </button>

            <button
              type="button"
              class="profile-edit-button"
              @click="abrirEditar"
            >
              Editar perfil
            </button>
          </div>
        </section>
      </main>
    </div>

    <!-- =====================================================
         MODAL EDITAR PERFIL
    ====================================================== -->

    <div
      v-if="mostrarEditar"
      class="profile-modal-overlay"
      @click.self="cerrarEditar"
    >
      <section class="profile-modal">
        <header class="profile-modal-header">
          <div>
            <p>
              DATOS PERSONALES
            </p>

            <h2>
              Editar mi perfil
            </h2>
          </div>

          <button
            type="button"
            @click="cerrarEditar"
          >
            ×
          </button>
        </header>

        <div class="profile-modal-body">
          <label>
            Nombre completo
            <span>*</span>
          </label>

          <input
            v-model.trim="form.nombre_completo"
            type="text"
          />

          <label>
            Correo institucional
          </label>

          <input
            v-model.trim="form.correo"
            type="email"
          />

          <label>
            Teléfono
          </label>

          <input
            v-model.trim="form.telefono"
            type="text"
            placeholder="Ej. 55555555"
          />

          <label>
            Fecha de nacimiento (opcional)
          </label>

          <input
            v-model="form.fecha_nacimiento"
            type="date"
          />
        </div>

        <footer class="profile-modal-footer">
          <button
            type="button"
            class="profile-modal-cancel"
            @click="cerrarEditar"
          >
            Cancelar
          </button>

          <button
            type="button"
            class="profile-modal-save"
            :disabled="guardando"
            @click="guardarCambios"
          >
            {{
              guardando
                ? "Guardando..."
                : "Guardar cambios"
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
  onBeforeUnmount,
  onMounted,
  reactive,
  ref,
} from "vue";

import {
  useRouter,
} from "vue-router";

import TeacherSidebar
  from "../../components/layout/TeacherSidebar.vue";

import TeacherTopbar
  from "../../components/layout/TeacherTopbar.vue";

import {
  actualizarPerfilDocente,
  cambiarFotoPerfilDocente,
  obtenerFotoPerfilDocente,
  obtenerPerfilDocente,
} from "../../services/docentePerfilService";

import "../../assets/css/teacher-profile.css";


const router = useRouter();

const perfil = ref(null);

const cargando = ref(true);
const guardando = ref(false);

const error = ref("");

const mostrarEditar = ref(false);

const fotoInput = ref(null);
const fotoUrl = ref(null);


const form = reactive({
  nombre_completo: "",
  correo: "",
  telefono: "",
  fecha_nacimiento: "",
});


const iniciales = computed(() => {
  if (!perfil.value) {
    return "D";
  }

  const nombre =
    perfil.value.nombres || "";

  const apellido =
    perfil.value.apellidos || "";

  return (
    `${nombre.charAt(0)}${apellido.charAt(0)}`
      .toUpperCase()
    || "D"
  );
});


const anioCiclo = computed(() => {
  const seccion =
    perfil.value?.secciones?.[0];

  if (
    seccion
    && seccion.id_ciclo
  ) {
    return (
      localStorage.getItem(
        "sgad_ciclo_anio"
      )
      || "seleccionado"
    );
  }

  return "seleccionado";
});


function obtenerIdCiclo() {
  const valor =
    localStorage.getItem(
      "sgad_ciclo"
    );

  const id =
    Number(valor);

  return Number.isNaN(id)
    ? null
    : id;
}


async function cargarPerfil() {
  cargando.value = true;
  error.value = "";

  try {
    const data =
      await obtenerPerfilDocente(
        obtenerIdCiclo()
      );

    perfil.value =
      data.perfil;

    await cargarFoto();

  } catch (err) {
    error.value =
      err.response?.data?.mensaje
      || "No fue posible cargar el perfil.";

  } finally {
    cargando.value = false;
  }
}


async function cargarFoto() {
  if (fotoUrl.value) {
    URL.revokeObjectURL(
      fotoUrl.value
    );

    fotoUrl.value = null;
  }

  if (
    !perfil.value?.foto_disponible
  ) {
    return;
  }

  try {
    const response =
      await obtenerFotoPerfilDocente();

    fotoUrl.value =
      URL.createObjectURL(
        response.data
      );

  } catch {
    fotoUrl.value = null;
  }
}


function abrirSelectorFoto() {
  fotoInput.value?.click();
}


async function seleccionarFoto(event) {
  const archivo =
    event.target.files?.[0];

  if (!archivo) {
    return;
  }

  try {
    await cambiarFotoPerfilDocente(
      archivo
    );

    perfil.value.foto_disponible =
      true;

    await cargarFoto();

    window.dispatchEvent(
      new Event(
        "sgad-perfil-actualizado"
      )
    );

    window.alert(
      "Foto de perfil actualizada correctamente."
    );

  } catch (err) {
    window.alert(
      err.response?.data?.mensaje
      || "No fue posible cambiar la foto."
    );
  }

  event.target.value = "";
}


function abrirEditar() {
  if (!perfil.value) {
    return;
  }

  form.nombre_completo =
    perfil.value.nombre_completo;

  form.correo =
    perfil.value.correo || "";

  form.telefono =
    perfil.value.telefono || "";

  form.fecha_nacimiento =
    perfil.value.fecha_nacimiento
    || "";

  mostrarEditar.value = true;
}


function cerrarEditar() {
  mostrarEditar.value = false;
}


function separarNombreCompleto() {
  const nombreCompleto =
    form.nombre_completo
      .trim()
      .replace(/\s+/g, " ");

  if (
    nombreCompleto
    === perfil.value.nombre_completo
  ) {
    return {
      nombres:
        perfil.value.nombres,

      apellidos:
        perfil.value.apellidos,
    };
  }

  const partes =
    nombreCompleto.split(" ");

  if (partes.length < 2) {
    return null;
  }

  if (partes.length === 2) {
    return {
      nombres:
        partes[0],

      apellidos:
        partes[1],
    };
  }

  if (partes.length === 3) {
    return {
      nombres:
        partes[0],

      apellidos:
        partes
          .slice(1)
          .join(" "),
    };
  }

  const mitad =
    Math.ceil(
      partes.length / 2
    );

  return {
    nombres:
      partes
        .slice(0, mitad)
        .join(" "),

    apellidos:
      partes
        .slice(mitad)
        .join(" "),
  };
}


async function guardarCambios() {
  const nombre =
    separarNombreCompleto();

  if (!nombre) {
    window.alert(
      "Ingrese nombre y apellido."
    );

    return;
  }

  guardando.value = true;

  try {
    const data =
      await actualizarPerfilDocente({
        nombres:
          nombre.nombres,

        apellidos:
          nombre.apellidos,

        correo:
          form.correo,

        telefono:
          form.telefono,

        fecha_nacimiento:
          form.fecha_nacimiento
          || null,

        id_ciclo:
          obtenerIdCiclo(),
      });

    perfil.value =
      data.perfil;

    const usuarioActual =
      JSON.parse(
        localStorage.getItem(
          "usuario"
        ) || "{}"
      );

    const usuarioNuevo = {
      ...usuarioActual,

      nombres:
        perfil.value.nombres,

      apellidos:
        perfil.value.apellidos,

      correo:
        perfil.value.correo,
    };

    localStorage.setItem(
      "usuario",
      JSON.stringify(
        usuarioNuevo
      )
    );

    cerrarEditar();

    window.dispatchEvent(
      new Event(
        "sgad-perfil-actualizado"
      )
    );

    window.alert(
      "Perfil actualizado correctamente."
    );

  } catch (err) {
    window.alert(
      err.response?.data?.mensaje
      || "No fue posible guardar los cambios."
    );

  } finally {
    guardando.value = false;
  }
}


function volverPanel() {
  router.push(
    "/docente/dashboard"
  );
}


function formatearFecha(valor) {
  if (!valor) {
    return "No registrada";
  }

  const fecha =
    new Date(
      `${valor}T00:00:00`
    );

  return fecha.toLocaleDateString(
    "es-GT",
    {
      day: "2-digit",
      month: "long",
      year: "numeric",
    }
  );
}


onMounted(
  cargarPerfil
);


onBeforeUnmount(() => {
  if (fotoUrl.value) {
    URL.revokeObjectURL(
      fotoUrl.value
    );
  }
});
</script>