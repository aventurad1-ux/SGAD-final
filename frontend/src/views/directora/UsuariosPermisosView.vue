<template>
  <div class="director-layout">
    <DirectorSidebar />

    <div class="director-main">
      <DirectorTopbar />

      <main class="director-content users-page">
        <!-- ==========================================
             ENCABEZADO
        =========================================== -->

        <section class="users-page-head">
          <div>
            <p class="users-eyebrow">
              ADMINISTRACIÓN
            </p>

            <h1>
              Usuarios y permisos
            </h1>

            <p class="users-page-description">
              Asigne accesos según la responsabilidad de cada persona.
            </p>
          </div>

          <button
            v-if="ciclo?.editable"
            type="button"
            class="users-primary-btn"
            @click="abrirCrearUsuario"
          >
            Crear usuario
          </button>
        </section>

        <!-- MENSAJES -->

        <div
          v-if="mensaje"
          class="users-alert users-alert-success"
        >
          {{ mensaje }}
        </div>

        <div
          v-if="error"
          class="users-alert users-alert-error"
        >
          {{ error }}
        </div>

        <!-- CICLO HISTÓRICO -->

        <div
          v-if="ciclo && !ciclo.editable"
          class="users-history-info"
        >
          <span>i</span>

          <p>
            El ciclo {{ ciclo.anio }} es histórico.
            Los usuarios pueden consultarse, pero no modificarse.
          </p>
        </div>

        <!-- ==========================================
             TABLA
        =========================================== -->

        <section class="users-table-card">
          <div
            v-if="cargando"
            class="users-empty"
          >
            Cargando usuarios...
          </div>

          <div
            v-else
            class="users-table-wrapper"
          >
            <table class="users-table">
              <thead>
                <tr>
                  <th>Usuario</th>
                  <th>Rol institucional</th>
                  <th>Alcance</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="usuario in usuarios"
                  :key="usuario.id_usuario"
                >
                  <td>
                    <div class="users-user-cell">
                      <strong>
                        {{ usuario.nombre }}
                      </strong>

                      <span>
                        {{ usuario.correo }}
                      </span>
                    </div>
                  </td>

                  <td>
                    {{ usuario.rol }}
                  </td>

                  <td>
                    {{ usuario.alcance }}
                  </td>

                  <td>
                    <span
                      class="users-status-badge"
                      :class="
                        usuario.activo
                          ? 'active'
                          : 'inactive'
                      "
                    >
                      {{
                        usuario.activo
                          ? "Activo"
                          : "Inactivo"
                      }}
                    </span>
                  </td>

                  <td>
                    <button
                      type="button"
                      class="users-admin-btn"
                      @click="abrirAdministrar(usuario)"
                    >
                      Administrar
                    </button>
                  </td>
                </tr>

                <tr v-if="!usuarios.length">
                  <td
                    colspan="5"
                    class="users-empty"
                  >
                    No existen usuarios registrados.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>

    <!-- ==========================================
         MODAL CREAR / ADMINISTRAR
    =========================================== -->

    <div
      v-if="modalUsuario"
      class="users-overlay"
      @click.self="cerrarModal"
    >
      <section class="users-modal">
        <!-- CABECERA -->

        <header class="users-modal-head">
          <div>
            <p>
              ADMINISTRACIÓN DE ACCESO
            </p>

            <h2>
              {{
                modoEdicion
                  ? "Administrar usuario"
                  : "Crear usuario"
              }}
            </h2>
          </div>

          <button
            type="button"
            class="users-modal-close"
            @click="cerrarModal"
          >
            ×
          </button>
        </header>

        <!-- CONTENIDO CON SCROLL -->

        <div class="users-modal-scroll">
          <!-- DATOS PRINCIPALES -->

          <div class="users-form-grid">
            <div class="users-form-group">
              <label class="required">
                Nombre completo
              </label>

              <input
                v-model.trim="formUsuario.nombreCompleto"
                type="text"
                class="users-input"
              />
            </div>

            <div class="users-form-group">
              <label class="required">
                Correo institucional
              </label>

              <input
                v-model.trim="formUsuario.correo"
                type="email"
                class="users-input"
              />
            </div>

            <div class="users-form-group">
              <label class="required">
                Rol
              </label>

              <select
                v-model="formUsuario.id_rol"
                class="users-input"
                :disabled="bloquearRol"
                @change="cambiarRol"
              >
                <option
                  v-for="rol in roles"
                  :key="rol.id_rol"
                  :value="String(rol.id_rol)"
                >
                  {{ rol.nombre }}
                </option>
              </select>
            </div>

            <div class="users-form-group">
              <label>
                Estado
              </label>

              <select
                v-model="formUsuario.activo"
                class="users-input"
                :disabled="esCuentaActual"
              >
                <option :value="true">
                  Activo
                </option>

                <option :value="false">
                  Inactivo
                </option>
              </select>
            </div>
          </div>

          <!-- ======================================
               DIRECTORA
          ======================================= -->

          <div
            v-if="rolSeleccionado?.nombre === 'Directora'"
            class="users-director-info"
          >
            <span>
              i
            </span>

            <p>
              La cuenta principal de Dirección conserva
              todos los permisos administrativos.
            </p>
          </div>

          <!-- ======================================
               SECCIONES DEL DOCENTE
          ======================================= -->

          <template
            v-if="rolSeleccionado?.nombre === 'Docente'"
          >
            <section class="users-modal-section">
              <h3>
                Secciones asignadas
              </h3>

              <div
                v-if="!secciones.length"
                class="users-empty-small"
              >
                No existen secciones disponibles.
              </div>

              <div
                v-else
                class="users-section-grid"
              >
                <label
                  v-for="seccion in secciones"
                  :key="seccion.id_seccion"
                  class="users-option-card"
                  :class="{
                    disabled: seccionOcupadaPorOtro(seccion)
                  }"
                >
                  <input
                    v-model="formUsuario.secciones"
                    type="checkbox"
                    :value="seccion.id_seccion"
                    :disabled="seccionOcupadaPorOtro(seccion)"
                  />

                  <span class="users-option-text">
                    <strong>
                      {{ seccion.etiqueta }}
                    </strong>

                    <small>
                      {{
                        seccion.docente
                          ? `Asignada a ${seccion.docente}`
                          : "Sin responsable"
                      }}
                    </small>
                  </span>
                </label>
              </div>
            </section>

            <!-- ====================================
                 PERMISOS
            ===================================== -->

            <section class="users-modal-section">
              <h3>
                Permisos individuales
              </h3>

              <div class="users-permission-grid">
                <label
                  v-for="permiso in permisosDocente"
                  :key="permiso.codigo"
                  class="users-option-card users-permission-card"
                >
                  <input
                    v-model="formUsuario.permisos"
                    type="checkbox"
                    :value="permiso.codigo"
                  />

                  <span class="users-option-text">
                    {{ nombrePermisoPrototipo(permiso) }}
                  </span>
                </label>
              </div>
            </section>
          </template>

          <!-- ======================================
               CONTRASEÑA REAL DEL SISTEMA
          ======================================= -->

          <section class="users-password-section">
            <div class="users-form-group">
              <label
                :class="{
                  required: !modoEdicion
                }"
              >
                {{
                  modoEdicion
                    ? "Nueva contraseña"
                    : "Contraseña temporal"
                }}
              </label>

              <input
                v-model="formUsuario.password"
                type="password"
                class="users-input"
                autocomplete="new-password"
                :placeholder="
                  modoEdicion
                    ? 'Dejar vacío para conservar la actual'
                    : 'Mínimo 10 caracteres'
                "
              />

              <small>
                {{
                  modoEdicion
                    ? "Solo complete este campo si desea cambiar la contraseña."
                    : "Esta contraseña permitirá al usuario ingresar al SGAD."
                }}
              </small>
            </div>
          </section>

          <div
            v-if="errorModal"
            class="users-alert users-alert-error users-modal-error"
          >
            {{ errorModal }}
          </div>
        </div>

        <!-- FOOTER FIJO -->

        <footer class="users-modal-footer">
          <button
            type="button"
            class="users-cancel-btn"
            @click="cerrarModal"
          >
            Cancelar
          </button>

          <button
            v-if="ciclo?.editable"
            type="button"
            class="users-save-btn"
            :disabled="procesando"
            @click="guardarUsuario"
          >
            {{
              procesando
                ? "Guardando..."
                : "Guardar usuario"
            }}
          </button>
        </footer>
      </section>
    </div>
  </div>
</template>

<script>
import DirectorSidebar
  from "../../components/layout/DirectorSidebar.vue";

import DirectorTopbar
  from "../../components/layout/DirectorTopbar.vue";

import {
  obtenerUsuarios,
  obtenerCatalogosUsuarios,
  crearUsuario,
  actualizarUsuario,
  cambiarEstadoUsuario
} from "../../services/usuariosService";

import "../../assets/css/usuarios-permisos.css";


export default {
  name: "UsuariosPermisosView",

  components: {
    DirectorSidebar,
    DirectorTopbar
  },

  data() {
    return {
      ciclo: null,

      usuarios: [],
      roles: [],
      permisos: [],
      secciones: [],

      cargando: true,
      procesando: false,

      mensaje: "",
      error: "",
      errorModal: "",

      modalUsuario: false,
      modoEdicion: false,
      usuarioEditando: null,

      formUsuario: {
        nombreCompleto: "",
        correo: "",
        id_rol: "",
        activo: true,
        password: "",
        secciones: [],
        permisos: []
      }
    };
  },

  computed: {
    rolSeleccionado() {
      return (
        this.roles.find(
          rol =>
            String(rol.id_rol) ===
            String(this.formUsuario.id_rol)
        ) || null
      );
    },

    permisosDocente() {
      const orden = [
        "estudiantes.ver",
        "documentos.ver",
        "documentos.subir",
        "documentos.actualizar",
        "solicitudes.ver",
        "solicitudes.entregar",
        "documentos.descargar",
        "solicitudes.comprobantes"
      ];

      return orden
        .map(
          codigo =>
            this.permisos.find(
              permiso =>
                permiso.codigo === codigo
            )
        )
        .filter(Boolean);
    },

    bloquearRol() {
      return (
        this.modoEdicion &&
        this.usuarioEditando?.rol ===
          "Directora"
      );
    },

    esCuentaActual() {
      if (!this.usuarioEditando) {
        return false;
      }

      try {
        const usuarioActual =
          JSON.parse(
            localStorage.getItem(
              "usuario"
            ) || "{}"
          );

        return (
          Number(
            usuarioActual.id_usuario
          ) ===
          Number(
            this.usuarioEditando.id_usuario
          )
        );
      } catch {
        return false;
      }
    }
  },

  async mounted() {
    await this.cargarTodo(
      this.obtenerCicloSeleccionado()
    );

    window.addEventListener(
      "sgad-cycle-changed",
      this.escucharCambioCiclo
    );
  },

  beforeUnmount() {
    window.removeEventListener(
      "sgad-cycle-changed",
      this.escucharCambioCiclo
    );
  },

  methods: {
    obtenerCicloSeleccionado() {
      const id =
        localStorage.getItem(
          "sgad_ciclo"
        );

      return id
        ? Number(id)
        : null;
    },

    async cargarTodo(
      idCiclo = null
    ) {
      this.cargando = true;
      this.error = "";

      try {
        const [
          usuariosData,
          catalogosData
        ] = await Promise.all([
          obtenerUsuarios(
            idCiclo
          ),

          obtenerCatalogosUsuarios(
            idCiclo
          )
        ]);

        this.ciclo =
          usuariosData.ciclo;

        this.usuarios =
          usuariosData.usuarios ||
          [];

        this.roles =
          catalogosData.roles ||
          [];

        this.permisos =
          catalogosData.permisos ||
          [];

        this.secciones =
          catalogosData.secciones ||
          [];

      } catch (error) {
        console.error(error);

        this.error =
          error.response?.data?.mensaje ||
          error.response?.data?.message ||
          "No fue posible cargar los usuarios.";

      } finally {
        this.cargando = false;
      }
    },

    async escucharCambioCiclo(
      event
    ) {
      const idCiclo =
        event.detail?.id_ciclo;

      if (!idCiclo) {
        return;
      }

      this.modalUsuario =
        false;

      await this.cargarTodo(
        Number(idCiclo)
      );
    },

    rolPorNombre(nombre) {
      return this.roles.find(
        rol =>
          rol.nombre === nombre
      );
    },

    permisosPorDefectoRol(
      idRol
    ) {
      const rol =
        this.roles.find(
          item =>
            String(item.id_rol) ===
            String(idRol)
        );

      return [
        ...(rol?.permisos || [])
      ];
    },

    abrirCrearUsuario() {
      const docente =
        this.rolPorNombre(
          "Docente"
        );

      this.modoEdicion =
        false;

      this.usuarioEditando =
        null;

      this.errorModal =
        "";

      this.formUsuario = {
        nombreCompleto: "",
        correo: "",

        id_rol:
          docente
            ? String(docente.id_rol)
            : "",

        activo: true,
        password: "",
        secciones: [],

        permisos:
          docente
            ? this.permisosPorDefectoRol(
                docente.id_rol
              )
            : []
      };

      this.modalUsuario =
        true;
    },

    abrirAdministrar(
      usuario
    ) {
      this.modoEdicion =
        true;

      this.usuarioEditando =
        usuario;

      this.errorModal =
        "";

      this.formUsuario = {
        nombreCompleto:
          usuario.nombre,

        correo:
          usuario.correo,

        id_rol:
          String(
            usuario.id_rol
          ),

        activo:
          Boolean(
            usuario.activo
          ),

        password: "",

        secciones:
          usuario.secciones.map(
            item =>
              item.id_seccion
          ),

        permisos: [
          ...usuario.permisos_efectivos
        ]
      };

      this.modalUsuario =
        true;
    },

    cerrarModal() {
      if (this.procesando) {
        return;
      }

      this.modalUsuario =
        false;

      this.usuarioEditando =
        null;

      this.errorModal =
        "";
    },

    cambiarRol() {
      this.formUsuario.secciones =
        [];

      this.formUsuario.permisos =
        this.permisosPorDefectoRol(
          this.formUsuario.id_rol
        );
    },

    seccionOcupadaPorOtro(
      seccion
    ) {
      if (!seccion.id_docente) {
        return false;
      }

      if (
        this.modoEdicion &&
        Number(
          seccion.id_docente
        ) ===
        Number(
          this.usuarioEditando?.id_usuario
        )
      ) {
        return false;
      }

      return true;
    },

    nombrePermisoPrototipo(
      permiso
    ) {
      const nombres = {
        "estudiantes.ver":
          "Ver estudiantes",

        "documentos.ver":
          "Ver expedientes",

        "documentos.subir":
          "Subir documentos de expediente",

        "documentos.actualizar":
          "Actualizar documentos",

        "solicitudes.ver":
          "Ver solicitudes",

        "solicitudes.entregar":
          "Realizar entregas",

        "documentos.descargar":
          "Descargar documentos",

        "solicitudes.comprobantes":
          "Consultar comprobantes"
      };

      return (
        nombres[
          permiso.codigo
        ] ||
        permiso.nombre
      );
    },

    separarNombreCompleto(
      nombreCompleto
    ) {
      const partes =
        nombreCompleto
          .trim()
          .split(/\s+/)
          .filter(Boolean);

      if (partes.length < 2) {
        return {
          nombres:
            partes[0] || "",

          apellidos:
            ""
        };
      }

      if (partes.length === 2) {
        return {
          nombres:
            partes[0],

          apellidos:
            partes[1]
        };
      }

      if (partes.length === 3) {
        return {
          nombres:
            partes[0],

          apellidos:
            `${partes[1]} ${partes[2]}`
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
            .join(" ")
      };
    },

    validarFormulario() {
      if (
        !this.formUsuario
          .nombreCompleto
          .trim()
      ) {
        this.errorModal =
          "Ingrese el nombre completo.";

        return false;
      }

      const nombreSeparado =
        this.separarNombreCompleto(
          this.formUsuario.nombreCompleto
        );

      if (
        !nombreSeparado.nombres ||
        !nombreSeparado.apellidos
      ) {
        this.errorModal =
          "Ingrese al menos un nombre y un apellido.";

        return false;
      }

      if (
        !this.formUsuario.correo
      ) {
        this.errorModal =
          "Ingrese el correo institucional.";

        return false;
      }

      if (
        !this.formUsuario.id_rol
      ) {
        this.errorModal =
          "Seleccione el rol.";

        return false;
      }

      if (
        !this.modoEdicion &&
        this.formUsuario.password.length
          < 10
      ) {
        this.errorModal =
          "La contraseña temporal debe tener al menos 10 caracteres.";

        return false;
      }

      if (
        this.formUsuario.password &&
        this.formUsuario.password.length
          < 10
      ) {
        this.errorModal =
          "La contraseña debe tener al menos 10 caracteres.";

        return false;
      }

      return true;
    },

    async guardarUsuario() {
      if (
        !this.validarFormulario()
      ) {
        return;
      }

      const nombre =
        this.separarNombreCompleto(
          this.formUsuario.nombreCompleto
        );

      this.procesando = true;
      this.errorModal = "";

      const payload = {
        id_ciclo:
          this.ciclo.id_ciclo,

        nombres:
          nombre.nombres,

        apellidos:
          nombre.apellidos,

        correo:
          this.formUsuario.correo,

        telefono: "",

        id_rol:
          Number(
            this.formUsuario.id_rol
          ),

        password:
          this.formUsuario.password,

        activo:
          Boolean(
            this.formUsuario.activo
          ),

        secciones:
          this.formUsuario.secciones,

        permisos:
          this.formUsuario.permisos
      };

      try {
        let respuesta;

        if (this.modoEdicion) {
          const estadoAnterior =
            Boolean(
              this.usuarioEditando.activo
            );

          respuesta =
            await actualizarUsuario(
              this.usuarioEditando.id_usuario,
              payload
            );

          const estadoNuevo =
            Boolean(
              this.formUsuario.activo
            );

          if (
            estadoAnterior !==
              estadoNuevo &&
            !this.esCuentaActual
          ) {
            await cambiarEstadoUsuario(
              this.usuarioEditando.id_usuario,
              estadoNuevo
            );
          }

        } else {
          respuesta =
            await crearUsuario(
              payload
            );
        }

        this.mensaje =
          respuesta.mensaje;

        this.modalUsuario =
          false;

        this.usuarioEditando =
          null;

        await this.cargarTodo(
          this.ciclo.id_ciclo
        );

      } catch (error) {
        console.error(error);

        this.errorModal =
          error.response?.data?.mensaje ||
          error.response?.data?.message ||
          "No fue posible guardar el usuario.";

      } finally {
        this.procesando =
          false;
      }
    }
  }
};
</script>