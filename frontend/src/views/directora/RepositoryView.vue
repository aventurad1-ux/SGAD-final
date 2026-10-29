<template>
  <div class="director-layout">
    <DirectorSidebar />

    <div class="director-main">
      <DirectorTopbar />

      <main class="director-content">
        <!-- ==================================================
             ENCABEZADO
        =================================================== -->

        <section class="records-page-head">
          <div>
            <p class="records-eyebrow">
              ARCHIVO DIGITAL
            </p>

            <h1>Repositorio institucional</h1>

            <p class="records-subtitle">
              Consulte y administre los documentos institucionales
              del ciclo {{ ciclo?.anio || "" }}.
            </p>
          </div>

          <div class="repo-head-actions">
            <button
              type="button"
              class="records-btn records-btn-secondary"
              @click="abrirCategorias"
            >
              Categorías
            </button>

            <button
              v-if="ciclo?.editable"
              type="button"
              class="records-btn records-btn-primary"
              @click="abrirSubirDocumento"
            >
              Subir documento
            </button>
          </div>
        </section>

        <!-- ==================================================
             MENSAJES DE ERROR
        =================================================== -->

        <div
          v-if="error"
          class="records-alert records-alert-error"
        >
          {{ error }}
        </div>

        <div
          v-if="ciclo && !ciclo.editable"
          class="records-info"
        >
          Está consultando el ciclo {{ ciclo.anio }}.
          Este ciclo es histórico y está disponible
          únicamente para consulta.
        </div>

        <!-- ==================================================
             FILTROS
        =================================================== -->

        <section class="repo-toolbar">
          <input
            v-model="filtros.buscar"
            type="text"
            class="records-input"
            placeholder="Buscar por código, título o responsable..."
            @input="programarBusqueda"
          />

          <select
            v-model="filtros.id_categoria"
            class="records-input"
            @change="cargarRepositorio"
          >
            <option value="">
              Todas las categorías
            </option>

            <option
              v-for="categoria in categorias"
              :key="categoria.id_categoria"
              :value="categoria.id_categoria"
            >
              {{ categoria.nombre }}
            </option>
          </select>

          <select
            v-model="filtros.estado"
            class="records-input"
            @change="cargarRepositorio"
          >
            <option value="">
              Todos los estados
            </option>

            <option value="Vigente">
              Vigente
            </option>

            <option value="Archivado">
              Archivado
            </option>
          </select>

          <select
            v-model="filtros.nivel_acceso"
            class="records-input"
            @change="cargarRepositorio"
          >
            <option value="">
              Todos los accesos
            </option>

            <option value="direccion">
              Solo Dirección
            </option>

            <option value="direccion_docentes">
              Dirección y docentes
            </option>
          </select>
        </section>

        <!-- ==================================================
             TABLA
        =================================================== -->

        <div
          v-if="cargando"
          class="records-empty"
        >
          Cargando repositorio...
        </div>

        <section
          v-else
          class="records-table-card"
        >
          <div class="records-table-wrap">
            <table class="repo-table">
              <thead>
                <tr>
                  <th>Documento</th>
                  <th>Categoría</th>
                  <th>Responsable</th>
                  <th>Fecha</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="documento in documentos"
                  :key="documento.id_documento"
                >
                  <td>
                    <div class="records-cell-title">
                      {{ documento.titulo }}
                    </div>

                    <div class="records-cell-sub">
                      {{ documento.codigo }}
                      ·
                      v{{ documento.version_actual }}
                    </div>

                    <div class="records-cell-sub">
                      {{ documento.nivel_acceso_texto }}
                    </div>
                  </td>

                  <td>
                    {{ documento.categoria }}
                  </td>

                  <td>
                    {{ documento.responsable }}
                  </td>

                  <td>
                    {{ formatearFecha(documento.fecha_documental) }}
                  </td>

                  <td>
                    <span
                      class="records-badge"
                      :class="
                        documento.estado === 'Vigente'
                          ? 'records-badge-success'
                          : 'repo-badge-archived'
                      "
                    >
                      {{ documento.estado }}
                    </span>
                  </td>

                  <td>
                    <div class="repo-table-actions">
                      <button
                        type="button"
                        class="records-btn records-btn-soft records-btn-sm"
                        @click="abrirFicha(documento)"
                      >
                        Ver ficha
                      </button>

                      <button
                        v-if="ciclo?.editable"
                        type="button"
                        class="records-btn records-btn-secondary records-btn-sm"
                        @click="abrirAdministrar(documento)"
                      >
                        Administrar
                      </button>
                    </div>
                  </td>
                </tr>

                <tr v-if="!documentos.length">
                  <td
                    colspan="6"
                    class="records-table-empty"
                  >
                    No hay documentos que coincidan con los filtros.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>

    <!-- ==================================================
         MODAL · CATEGORÍAS
    =================================================== -->

    <div
      v-if="modalCategorias"
      class="records-overlay"
      @click.self="cerrarCategorias"
    >
      <section class="records-modal repo-modal-categories">
        <header class="records-modal-head">
          <div>
            <p>REPOSITORIO INSTITUCIONAL</p>

            <h2>Categorías</h2>
          </div>

          <button
            type="button"
            class="records-close"
            @click="cerrarCategorias"
          >
            ×
          </button>
        </header>

        <div class="records-modal-body">
          <div
            v-if="ciclo?.editable"
            class="repo-new-category"
          >
            <input
              v-model.trim="nuevaCategoria"
              type="text"
              class="records-input"
              placeholder="Nombre de la nueva categoría"
              @keyup.enter="guardarCategoria"
            />

            <button
              type="button"
              class="records-btn records-btn-primary"
              :disabled="procesando"
              @click="guardarCategoria"
            >
              Agregar
            </button>
          </div>

          <div
            v-if="errorModal"
            class="records-alert records-alert-error"
          >
            {{ errorModal }}
          </div>

          <section class="repo-category-list">
            <article
              v-for="categoria in categorias"
              :key="categoria.id_categoria"
              class="repo-category-item"
            >
              <div>
                <strong>
                  {{ categoria.nombre }}
                </strong>

                <span
                  class="repo-category-status"
                  :class="{
                    active: categoria.activa
                  }"
                >
                  {{
                    categoria.activa
                      ? "Activa"
                      : "Inactiva"
                  }}
                </span>
              </div>

              <button
                v-if="ciclo?.editable"
                type="button"
                class="records-btn records-btn-secondary records-btn-sm"
                :disabled="procesando"
                @click="cambiarEstadoCategoria(categoria)"
              >
                {{
                  categoria.activa
                    ? "Desactivar"
                    : "Activar"
                }}
              </button>
            </article>
          </section>
        </div>

        <footer class="records-modal-footer">
          <button
            type="button"
            class="records-btn records-btn-secondary"
            @click="cerrarCategorias"
          >
            Cerrar
          </button>
        </footer>
      </section>
    </div>

    <!-- ==================================================
         MODAL · SUBIR DOCUMENTO
    =================================================== -->

    <div
      v-if="modalSubir"
      class="records-overlay"
      @click.self="cerrarSubirDocumento"
    >
      <section class="records-modal records-modal-lg">
        <header class="records-modal-head">
          <div>
            <p>REPOSITORIO INSTITUCIONAL</p>

            <h2>Subir documento</h2>
          </div>

          <button
            type="button"
            class="records-close"
            @click="cerrarSubirDocumento"
          >
            ×
          </button>
        </header>

        <div class="records-modal-body">
          <div class="records-form-group">
            <label class="required">
              Tipo de documento
            </label>

            <select
              v-model="tipoDocumento"
              class="records-input"
              @change="cambiarTipoDocumento"
            >
              <option value="institucional">
                Documento institucional
              </option>

              <option value="expediente">
                Documento de expediente estudiantil
              </option>
            </select>
          </div>

          <!-- DOCUMENTO INSTITUCIONAL -->

          <template v-if="tipoDocumento === 'institucional'">
            <div class="records-form-group">
              <label class="required">
                Título
              </label>

              <input
                v-model.trim="formInstitucional.titulo"
                type="text"
                class="records-input"
              />
            </div>

            <div class="records-form-two">
              <div class="records-form-group">
                <label class="required">
                  Categoría
                </label>

                <select
                  v-model="formInstitucional.id_categoria"
                  class="records-input"
                >
                  <option value="">
                    Seleccione...
                  </option>

                  <option
                    v-for="categoria in categoriasActivas"
                    :key="categoria.id_categoria"
                    :value="categoria.id_categoria"
                  >
                    {{ categoria.nombre }}
                  </option>
                </select>
              </div>

              <div class="records-form-group">
                <label class="required">
                  Nivel de acceso
                </label>

                <select
                  v-model="formInstitucional.nivel_acceso"
                  class="records-input"
                >
                  <option value="">
                    Seleccione...
                  </option>

                  <option value="direccion">
                    Solo Dirección
                  </option>

                  <option value="direccion_docentes">
                    Dirección y docentes
                  </option>
                </select>
              </div>
            </div>

            <div class="records-form-group">
              <label class="required">
                Fecha documental
              </label>

              <input
                v-model="formInstitucional.fecha_documental"
                type="date"
                class="records-input"
              />
            </div>

            <div class="records-form-group">
              <label class="required">
                Archivo digital
              </label>

              <input
                ref="archivoInstitucional"
                type="file"
                class="records-input records-file-input"
                accept=".pdf,.docx,.xlsx,.jpg,.jpeg,.png"
                @change="seleccionarArchivoInstitucional"
              />
            </div>

            <div class="records-form-group">
              <label>
                Descripción / observaciones
              </label>

              <textarea
                v-model.trim="formInstitucional.descripcion"
                class="records-input records-observations"
              ></textarea>
            </div>
          </template>

          <!-- EXPEDIENTE ESTUDIANTIL -->

          <template v-else>
            <div class="records-form-group">
              <label class="required">
                Grado y sección
              </label>

              <select
                v-model="formExpediente.id_seccion"
                class="records-input"
                @change="cambiarSeccionExpediente"
              >
                <option value="">
                  Seleccione...
                </option>

                <option
                  v-for="seccion in seccionesExpediente"
                  :key="seccion.id_seccion"
                  :value="seccion.id_seccion"
                >
                  {{ seccion.etiqueta }}
                </option>
              </select>
            </div>

            <div class="records-form-group">
              <label class="required">
                Buscar estudiante
              </label>

              <input
                v-model.trim="buscarEstudiante"
                type="text"
                class="records-input"
                placeholder="Escriba nombre, código o CUI..."
                :disabled="!formExpediente.id_seccion"
              />

              <div
                v-if="
                  formExpediente.id_seccion &&
                  buscarEstudiante &&
                  estudiantesExpedienteFiltrados.length
                "
                class="repo-student-results"
              >
                <button
                  v-for="estudiante in estudiantesExpedienteFiltrados"
                  :key="estudiante.id_estudiante"
                  type="button"
                  class="repo-student-option"
                  @click="seleccionarEstudiante(estudiante)"
                >
                  <strong>
                    {{ estudiante.nombre }}
                  </strong>

                  <span>
                    {{ estudiante.codigo }}
                    ·
                    {{ estudiante.cui }}
                  </span>
                </button>
              </div>
            </div>

            <div
              v-if="estudianteSeleccionado"
              class="records-student-notice"
            >
              <span class="records-info-icon">
                i
              </span>

              <span>
                Estudiante seleccionado:
                <strong>
                  {{ estudianteSeleccionado.nombre }}
                </strong>
              </span>
            </div>

            <div class="records-form-group">
              <label class="required">
                Documento del expediente
              </label>

              <select
                v-model="formExpediente.id_requisito"
                class="records-input"
                :disabled="!detalleEstudiante"
              >
                <option value="">
                  Seleccione...
                </option>

                <option
                  v-for="requisito in requisitosEstudiante"
                  :key="requisito.id_requisito"
                  :value="requisito.id_requisito"
                >
                  {{ requisito.nombre }}
                  {{
                    requisito.entregado
                      ? "· entregado · se creará nueva versión"
                      : "· pendiente"
                  }}
                </option>
              </select>
            </div>

            <div class="records-form-group">
              <label class="required">
                Archivo digital
              </label>

              <input
                ref="archivoExpedienteRepo"
                type="file"
                class="records-input records-file-input"
                accept=".pdf,.docx,.xlsx,.jpg,.jpeg,.png"
                @change="seleccionarArchivoExpediente"
              />
            </div>

            <div class="records-form-group">
              <label>
                Observaciones
              </label>

              <textarea
                v-model.trim="formExpediente.observaciones"
                class="records-input records-observations"
              ></textarea>
            </div>

            <div class="records-info repo-version-note">
              Los documentos ya entregados se actualizan
              como una nueva versión.
            </div>
          </template>

          <p class="records-file-help">
            Formatos permitidos: PDF, DOCX, XLSX, JPG, JPEG y PNG.
            Tamaño máximo: 10 MB.
          </p>

          <div
            v-if="errorModal"
            class="records-alert records-alert-error"
          >
            {{ errorModal }}
          </div>
        </div>

        <footer class="records-modal-footer">
          <button
            type="button"
            class="records-btn records-btn-secondary"
            :disabled="procesando"
            @click="cerrarSubirDocumento"
          >
            Cancelar
          </button>

          <button
            type="button"
            class="records-btn records-btn-primary"
            :disabled="procesando"
            @click="guardarDocumento"
          >
            {{
              procesando
                ? "Guardando..."
                : "Guardar documento"
            }}
          </button>
        </footer>
      </section>
    </div>

    <!-- ==================================================
         MODAL · FICHA
    =================================================== -->

    <div
      v-if="modalFicha"
      class="records-overlay"
      @click.self="cerrarFicha"
    >
      <section class="records-modal records-modal-xl">
        <header class="records-modal-head">
          <div>
            <p>REPOSITORIO INSTITUCIONAL</p>

            <h2>Ficha del documento</h2>
          </div>

          <button
            type="button"
            class="records-close"
            @click="cerrarFicha"
          >
            ×
          </button>
        </header>

        <div
          v-if="cargandoDetalle"
          class="records-modal-body"
        >
          <div class="records-empty">
            Cargando documento...
          </div>
        </div>

        <div
          v-else-if="detalleDocumento"
          class="records-modal-body"
        >
          <section class="records-detail-grid">
            <div class="records-detail-item">
              <label>CÓDIGO</label>
              <strong>{{ detalleDocumento.codigo }}</strong>
            </div>

            <div class="records-detail-item">
              <label>TÍTULO</label>
              <strong>{{ detalleDocumento.titulo }}</strong>
            </div>

            <div class="records-detail-item">
              <label>CATEGORÍA</label>
              <strong>{{ detalleDocumento.categoria }}</strong>
            </div>

            <div class="records-detail-item">
              <label>RESPONSABLE</label>
              <strong>{{ detalleDocumento.responsable }}</strong>
            </div>

            <div class="records-detail-item">
              <label>FECHA DOCUMENTAL</label>

              <strong>
                {{
                  formatearFecha(
                    detalleDocumento.fecha_documental
                  )
                }}
              </strong>
            </div>

            <div class="records-detail-item">
              <label>ESTADO</label>
              <strong>{{ detalleDocumento.estado }}</strong>
            </div>

            <div class="records-detail-item">
              <label>NIVEL DE ACCESO</label>
              <strong>{{ detalleDocumento.nivel_acceso_texto }}</strong>
            </div>

            <div class="records-detail-item">
              <label>VERSIÓN ACTUAL</label>
              <strong>v{{ detalleDocumento.version_actual }}</strong>
            </div>

            <div class="records-detail-item">
              <label>ARCHIVO</label>

              <strong>
                {{
                  detalleDocumento.archivo?.nombre_archivo
                  || "Sin archivo"
                }}
              </strong>
            </div>

            <div class="records-detail-item">
              <label>FORMATO</label>

              <strong>
                {{
                  obtenerFormato(
                    detalleDocumento.archivo?.nombre_archivo
                  )
                }}
              </strong>
            </div>

            <div class="records-detail-item">
              <label>TAMAÑO</label>

              <strong>
                {{
                  formatearTamano(
                    detalleDocumento.archivo?.tamano_bytes
                  )
                }}
              </strong>
            </div>

            <div class="records-detail-item">
              <label>CICLO ESCOLAR</label>
              <strong>{{ detalleDocumento.ciclo }}</strong>
            </div>
          </section>

          <div class="repo-description-block">
            <label>
              DESCRIPCIÓN / OBSERVACIONES
            </label>

            <p>
              {{
                detalleDocumento.descripcion
                || "Sin observaciones."
              }}
            </p>
          </div>

          <div class="repo-file-actions">
            <button
              v-if="
                puedePrevisualizar(
                  detalleDocumento.archivo?.tipo_mime
                )
              "
              type="button"
              class="records-btn records-btn-soft"
              @click="visualizarDocumentoActual"
            >
              Ver archivo
            </button>

            <button
              type="button"
              class="records-btn records-btn-secondary"
              @click="descargarDocumentoActual"
            >
              Descargar
            </button>
          </div>

          <h3 class="records-list-title repo-history-title">
            Historial de versiones
          </h3>

          <section class="repo-version-list">
            <article
              v-for="version in detalleDocumento.versiones"
              :key="version.id_version"
              class="repo-version-item"
            >
              <div>
                <strong>
                  Versión {{ version.numero_version }}
                </strong>

                <p>
                  {{ version.nombre_archivo }}
                  ·
                  {{ formatearFechaHora(version.fecha_subida) }}
                </p>

                <p v-if="version.motivo">
                  Motivo:
                  {{ version.motivo }}
                </p>

                <p>
                  Responsable:
                  {{ version.responsable }}
                </p>
              </div>

              <button
                type="button"
                class="records-btn records-btn-secondary records-btn-sm"
                @click="descargarVersion(version)"
              >
                Descargar
              </button>
            </article>

            <div
              v-if="!detalleDocumento.versiones?.length"
              class="records-muted"
            >
              No hay versiones registradas.
            </div>
          </section>
        </div>

        <footer class="records-modal-footer">
          <button
            type="button"
            class="records-btn records-btn-secondary"
            @click="cerrarFicha"
          >
            Cerrar
          </button>
        </footer>
      </section>
    </div>

    <!-- ==================================================
         MODAL · ADMINISTRAR
    =================================================== -->

    <div
      v-if="modalAdministrar"
      class="records-overlay"
      @click.self="cerrarAdministrar"
    >
      <section class="records-modal repo-admin-modal">
        <header class="records-modal-head repo-admin-head">
          <div>
            <p>ADMINISTRAR DOCUMENTO</p>

            <h2>
              {{ documentoAdministrar?.codigo }}
            </h2>
          </div>

          <button
            type="button"
            class="records-close"
            @click="cerrarAdministrar"
          >
            ×
          </button>
        </header>

        <div class="records-modal-body repo-admin-body">
          <p class="repo-admin-intro">
            Seleccione la acción que desea realizar sobre
            <strong>
              {{ documentoAdministrar?.titulo }}
            </strong>.
          </p>

          <div class="repo-admin-actions">
            <button
              type="button"
              class="repo-admin-button repo-admin-button-soft"
              @click="abrirEditarMetadatos"
            >
              Editar metadatos
            </button>

            <button
              type="button"
              class="repo-admin-button repo-admin-button-soft"
              @click="abrirReemplazarArchivo"
            >
              Reemplazar archivo
            </button>

            <button
              type="button"
              class="repo-admin-button repo-admin-button-secondary"
              @click="abrirFichaDesdeAdmin"
            >
              Ver ficha
            </button>

            <button
              type="button"
              class="repo-admin-button repo-admin-button-danger"
              @click="abrirConfirmarPapelera"
            >
              Enviar a papelera
            </button>
          </div>
        </div>

        <footer class="records-modal-footer">
          <button
            type="button"
            class="records-btn records-btn-secondary"
            @click="cerrarAdministrar"
          >
            Cerrar
          </button>
        </footer>
      </section>
    </div>

    <!-- ==================================================
         MODAL · EDITAR METADATOS
    =================================================== -->

    <div
      v-if="modalEditar"
      class="records-overlay records-overlay-front"
      @click.self="cerrarEditar"
    >
      <section class="records-modal records-upload-modal">
        <header class="records-modal-head">
          <div>
            <p>REPOSITORIO INSTITUCIONAL</p>
            <h2>Editar metadatos</h2>
          </div>

          <button
            type="button"
            class="records-close"
            @click="cerrarEditar"
          >
            ×
          </button>
        </header>

        <div class="records-modal-body">
          <div class="records-form-group">
            <label class="required">
              Título
            </label>

            <input
              v-model.trim="formEditar.titulo"
              class="records-input"
            />
          </div>

          <div class="records-form-group">
            <label class="required">
              Categoría
            </label>

            <select
              v-model="formEditar.id_categoria"
              class="records-input"
            >
              <option
                v-for="categoria in categorias"
                :key="categoria.id_categoria"
                :value="categoria.id_categoria"
              >
                {{ categoria.nombre }}
              </option>
            </select>
          </div>

          <div class="records-form-two">
            <div class="records-form-group">
              <label class="required">
                Estado
              </label>

              <select
                v-model="formEditar.estado"
                class="records-input"
              >
                <option value="Vigente">
                  Vigente
                </option>

                <option value="Archivado">
                  Archivado
                </option>
              </select>
            </div>

            <div class="records-form-group">
              <label class="required">
                Nivel de acceso
              </label>

              <select
                v-model="formEditar.nivel_acceso"
                class="records-input"
              >
                <option value="direccion">
                  Solo Dirección
                </option>

                <option value="direccion_docentes">
                  Dirección y docentes
                </option>
              </select>
            </div>
          </div>

          <div class="records-form-group">
            <label>
              Descripción
            </label>

            <textarea
              v-model.trim="formEditar.descripcion"
              class="records-input records-observations"
            ></textarea>
          </div>

          <div
            v-if="errorModal"
            class="records-alert records-alert-error"
          >
            {{ errorModal }}
          </div>
        </div>

        <footer class="records-modal-footer">
          <button
            type="button"
            class="records-btn records-btn-secondary"
            :disabled="procesando"
            @click="cerrarEditar"
          >
            Cancelar
          </button>

          <button
            type="button"
            class="records-btn records-btn-primary"
            :disabled="procesando"
            @click="guardarMetadatos"
          >
            {{
              procesando
                ? "Guardando..."
                : "Guardar cambios"
            }}
          </button>
        </footer>
      </section>
    </div>

    <!-- ==================================================
         MODAL · REEMPLAZAR ARCHIVO
    =================================================== -->

    <div
      v-if="modalReemplazar"
      class="records-overlay records-overlay-front"
      @click.self="cerrarReemplazar"
    >
      <section class="records-modal records-upload-modal">
        <header class="records-modal-head">
          <div>
            <p>REPOSITORIO INSTITUCIONAL</p>
            <h2>Reemplazar archivo</h2>
          </div>

          <button
            type="button"
            class="records-close"
            @click="cerrarReemplazar"
          >
            ×
          </button>
        </header>

        <div class="records-modal-body">
          <div class="records-info">
            Se conservará la versión actual y el nuevo archivo
            se registrará como una nueva versión.
          </div>

          <div class="records-form-group">
            <label class="required">
              Nuevo archivo
            </label>

            <input
              ref="archivoReemplazo"
              type="file"
              class="records-input records-file-input"
              accept=".pdf,.docx,.xlsx,.jpg,.jpeg,.png"
              @change="seleccionarArchivoReemplazo"
            />
          </div>

          <div class="records-form-group">
            <label class="required">
              Motivo del reemplazo
            </label>

            <textarea
              v-model.trim="formReemplazo.motivo"
              class="records-input records-observations"
              placeholder="Explique brevemente por qué se reemplaza el archivo."
            ></textarea>
          </div>

          <p class="records-file-help">
            Formatos permitidos: PDF, DOCX, XLSX,
            JPG, JPEG y PNG. Máximo 10 MB.
          </p>

          <div
            v-if="errorModal"
            class="records-alert records-alert-error"
          >
            {{ errorModal }}
          </div>
        </div>

        <footer class="records-modal-footer">
          <button
            type="button"
            class="records-btn records-btn-secondary"
            :disabled="procesando"
            @click="cerrarReemplazar"
          >
            Cancelar
          </button>

          <button
            type="button"
            class="records-btn records-btn-primary"
            :disabled="procesando"
            @click="guardarReemplazo"
          >
            {{
              procesando
                ? "Guardando..."
                : "Guardar nueva versión"
            }}
          </button>
        </footer>
      </section>
    </div>

    <!-- ==================================================
         MODAL · PAPELERA
    =================================================== -->

    <div
      v-if="modalPapelera"
      class="records-overlay records-overlay-front"
      @click.self="cerrarConfirmarPapelera"
    >
      <section class="records-modal repo-confirm-modal">
        <header class="records-modal-head">
          <div>
            <p>REPOSITORIO INSTITUCIONAL</p>
            <h2>Enviar a papelera</h2>
          </div>

          <button
            type="button"
            class="records-close"
            @click="cerrarConfirmarPapelera"
          >
            ×
          </button>
        </header>

        <div class="records-modal-body">
          <p class="repo-confirm-text">
            ¿Desea enviar
            <strong>
              {{ documentoAdministrar?.titulo }}
            </strong>
            a la papelera?
          </p>

          <p class="records-muted">
            El documento dejará de aparecer en el repositorio,
            pero podrá restaurarse posteriormente desde Papelera.
          </p>

          <div
            v-if="errorModal"
            class="records-alert records-alert-error"
          >
            {{ errorModal }}
          </div>
        </div>

        <footer class="records-modal-footer">
          <button
            type="button"
            class="records-btn records-btn-secondary"
            :disabled="procesando"
            @click="cerrarConfirmarPapelera"
          >
            Cancelar
          </button>

          <button
            type="button"
            class="repo-danger-button"
            :disabled="procesando"
            @click="confirmarPapelera"
          >
            {{
              procesando
                ? "Enviando..."
                : "Enviar a papelera"
            }}
          </button>
        </footer>
      </section>
    </div>

    <!-- ==================================================
         TOAST DE ÉXITO
    =================================================== -->

    <div
      v-if="mensaje"
      class="repo-toast"
    >
      <span class="repo-toast-check">
        ✓
      </span>

      <span class="repo-toast-text">
        {{ mensaje }}
      </span>

      <button
        type="button"
        class="repo-toast-close"
        @click="cerrarToast"
      >
        ×
      </button>
    </div>
  </div>
</template>

<script>
import DirectorSidebar from "../../components/layout/DirectorSidebar.vue";
import DirectorTopbar from "../../components/layout/DirectorTopbar.vue";

import {
  obtenerDocumentosRepositorio,
  obtenerCategoriasRepositorio,
  crearCategoriaRepositorio,
  cambiarEstadoCategoriaRepositorio,
  obtenerDetalleDocumentoRepositorio,
  subirDocumentoRepositorio,
  actualizarDocumentoRepositorio,
  reemplazarArchivoRepositorio,
  enviarDocumentoPapelera,
  verDocumentoRepositorio,
  descargarDocumentoRepositorio,
  descargarVersionRepositorio
} from "../../services/repositorioService";

import {
  obtenerExpedientes,
  obtenerDetalleExpediente,
  subirDocumento
} from "../../services/expedientesService";

import "../../assets/css/expedientes.css";
import "../../assets/css/repositorio.css";


export default {
  name: "RepositoryView",

  components: {
    DirectorSidebar,
    DirectorTopbar
  },

  data() {
    return {
      ciclo: null,

      documentos: [],
      categorias: [],

      cargando: true,
      cargandoDetalle: false,
      procesando: false,

      mensaje: "",
      error: "",
      errorModal: "",

      filtros: {
        buscar: "",
        id_categoria: "",
        estado: "",
        nivel_acceso: ""
      },

      temporizadorBusqueda: null,
      temporizadorToast: null,

      modalCategorias: false,
      modalSubir: false,
      modalFicha: false,
      modalAdministrar: false,
      modalEditar: false,
      modalReemplazar: false,
      modalPapelera: false,

      nuevaCategoria: "",

      tipoDocumento: "institucional",

      formInstitucional: {
        titulo: "",
        id_categoria: "",
        nivel_acceso: "",
        fecha_documental: "",
        descripcion: "",
        archivo: null
      },

      seccionesExpediente: [],
      estudiantesExpediente: [],

      buscarEstudiante: "",
      estudianteSeleccionado: null,
      detalleEstudiante: null,

      formExpediente: {
        id_seccion: "",
        id_requisito: "",
        observaciones: "",
        archivo: null
      },

      detalleDocumento: null,
      documentoAdministrar: null,

      formEditar: {
        titulo: "",
        id_categoria: "",
        estado: "Vigente",
        nivel_acceso: "direccion",
        descripcion: ""
      },

      formReemplazo: {
        archivo: null,
        motivo: ""
      }
    };
  },

  computed: {
    categoriasActivas() {
      return this.categorias.filter(
        categoria => categoria.activa
      );
    },


    estudiantesExpedienteFiltrados() {
      if (!this.formExpediente.id_seccion) {
        return [];
      }

      const texto =
        this.buscarEstudiante
          .trim()
          .toLowerCase();

      if (!texto) {
        return [];
      }

      return this.estudiantesExpediente
        .filter(
          estudiante =>
            Number(estudiante.id_seccion) ===
            Number(this.formExpediente.id_seccion)
        )
        .filter(estudiante => {
          const nombre =
            (estudiante.nombre || "")
              .toLowerCase();

          const codigo =
            (estudiante.codigo || "")
              .toLowerCase();

          const cui =
            (estudiante.cui || "")
              .toLowerCase();

          return (
            nombre.includes(texto) ||
            codigo.includes(texto) ||
            cui.includes(texto)
          );
        })
        .slice(0, 8);
    },


    requisitosEstudiante() {
      return (
        this.detalleEstudiante?.requisitos || []
      );
    }
  },


  async mounted() {
    window.addEventListener(
      "sgad-cycle-changed",
      this.manejarCambioCiclo
    );

    await this.cargarCategorias();
    await this.cargarRepositorio();
  },


  beforeUnmount() {
    window.removeEventListener(
      "sgad-cycle-changed",
      this.manejarCambioCiclo
    );

    if (this.temporizadorBusqueda) {
      clearTimeout(
        this.temporizadorBusqueda
      );
    }

    if (this.temporizadorToast) {
      clearTimeout(
        this.temporizadorToast
      );
    }
  },


  methods: {
    mostrarToast(texto) {
      this.mensaje =
        texto || "";

      if (this.temporizadorToast) {
        clearTimeout(
          this.temporizadorToast
        );
      }

      if (this.mensaje) {
        this.temporizadorToast =
          setTimeout(() => {
            this.mensaje = "";
            this.temporizadorToast = null;
          }, 4000);
      }
    },


    cerrarToast() {
      this.mensaje = "";

      if (this.temporizadorToast) {
        clearTimeout(
          this.temporizadorToast
        );

        this.temporizadorToast = null;
      }
    },


    obtenerIdCicloSeleccionado() {
      const valor =
        localStorage.getItem(
          "sgad_ciclo"
        );

      if (!valor) {
        return null;
      }

      try {
        const parsed =
          JSON.parse(valor);

        if (
          typeof parsed === "number"
        ) {
          return parsed;
        }

        if (
          parsed &&
          typeof parsed === "object"
        ) {
          return Number(
            parsed.id_ciclo ||
            parsed.id ||
            0
          ) || null;
        }

      } catch {
        const numero =
          Number(valor);

        return numero || null;
      }

      return null;
    },


    async manejarCambioCiclo() {
      this.filtros.buscar = "";
      this.filtros.id_categoria = "";
      this.filtros.estado = "";
      this.filtros.nivel_acceso = "";

      await this.cargarRepositorio();
    },


    programarBusqueda() {
      if (this.temporizadorBusqueda) {
        clearTimeout(
          this.temporizadorBusqueda
        );
      }

      this.temporizadorBusqueda =
        setTimeout(() => {
          this.cargarRepositorio();
        }, 350);
    },


    async cargarRepositorio() {
      this.cargando = true;
      this.error = "";

      try {
        const idCiclo =
          this.obtenerIdCicloSeleccionado();

        const data =
          await obtenerDocumentosRepositorio({
            id_ciclo:
              idCiclo,

            buscar:
              this.filtros.buscar,

            id_categoria:
              this.filtros.id_categoria,

            estado:
              this.filtros.estado,

            nivel_acceso:
              this.filtros.nivel_acceso
          });

        this.ciclo =
          data.ciclo || null;

        this.documentos =
          data.documentos || [];

      } catch (error) {
        console.error(error);

        this.error =
          error.response?.data?.mensaje ||
          "No fue posible cargar el repositorio.";

      } finally {
        this.cargando = false;
      }
    },


    async cargarCategorias() {
      try {
        const data =
          await obtenerCategoriasRepositorio();

        this.categorias =
          data.categorias || [];

      } catch (error) {
        console.error(error);

        this.error =
          error.response?.data?.mensaje ||
          "No fue posible cargar las categorías.";
      }
    },


    abrirCategorias() {
      this.errorModal = "";
      this.nuevaCategoria = "";
      this.modalCategorias = true;
    },


    cerrarCategorias() {
      if (this.procesando) {
        return;
      }

      this.modalCategorias = false;
      this.errorModal = "";
      this.nuevaCategoria = "";
    },


    async guardarCategoria() {
      if (!this.nuevaCategoria) {
        this.errorModal =
          "Escriba el nombre de la categoría.";

        return;
      }

      this.procesando = true;
      this.errorModal = "";

      try {
        const respuesta =
          await crearCategoriaRepositorio(
            this.nuevaCategoria
          );

        this.mostrarToast(
          respuesta.mensaje
        );

        this.nuevaCategoria = "";

        await this.cargarCategorias();

      } catch (error) {
        console.error(error);

        this.errorModal =
          error.response?.data?.mensaje ||
          "No fue posible crear la categoría.";

      } finally {
        this.procesando = false;
      }
    },


    async cambiarEstadoCategoria(
      categoria
    ) {
      this.procesando = true;
      this.errorModal = "";

      try {
        const respuesta =
          await cambiarEstadoCategoriaRepositorio(
            categoria.id_categoria,
            !categoria.activa
          );

        this.mostrarToast(
          respuesta.mensaje
        );

        await this.cargarCategorias();

      } catch (error) {
        console.error(error);

        this.errorModal =
          error.response?.data?.mensaje ||
          "No fue posible cambiar la categoría.";

      } finally {
        this.procesando = false;
      }
    },


    async abrirSubirDocumento() {
      this.resetFormularioSubida();

      this.modalSubir = true;

      await this.cargarDatosExpedientes();
    },


    cerrarSubirDocumento() {
      if (this.procesando) {
        return;
      }

      this.modalSubir = false;
      this.errorModal = "";

      this.resetFormularioSubida();
    },


    resetFormularioSubida() {
      this.tipoDocumento =
        "institucional";

      this.formInstitucional = {
        titulo: "",
        id_categoria: "",
        nivel_acceso: "",

        fecha_documental:
          new Date()
            .toISOString()
            .slice(0, 10),

        descripcion: "",
        archivo: null
      };

      this.formExpediente = {
        id_seccion: "",
        id_requisito: "",
        observaciones: "",
        archivo: null
      };

      this.buscarEstudiante = "";
      this.estudianteSeleccionado = null;
      this.detalleEstudiante = null;

      this.errorModal = "";
    },


    cambiarTipoDocumento() {
      this.errorModal = "";

      this.buscarEstudiante = "";
      this.estudianteSeleccionado = null;
      this.detalleEstudiante = null;

      this.formExpediente = {
        id_seccion: "",
        id_requisito: "",
        observaciones: "",
        archivo: null
      };
    },


    async cargarDatosExpedientes() {
      try {
        const idCiclo =
          this.ciclo?.id_ciclo ||
          this.obtenerIdCicloSeleccionado();

        const data =
          await obtenerExpedientes(
            idCiclo
          );

        this.seccionesExpediente =
          data.secciones || [];

        this.estudiantesExpediente =
          data.estudiantes || [];

      } catch (error) {
        console.error(error);

        this.errorModal =
          "No fue posible cargar los datos de expedientes.";
      }
    },


    cambiarSeccionExpediente() {
      this.buscarEstudiante = "";
      this.estudianteSeleccionado = null;
      this.detalleEstudiante = null;

      this.formExpediente.id_requisito =
        "";
    },


    async seleccionarEstudiante(
      estudiante
    ) {
      this.estudianteSeleccionado =
        estudiante;

      this.buscarEstudiante =
        estudiante.nombre;

      this.formExpediente.id_requisito =
        "";

      this.errorModal = "";

      try {
        this.detalleEstudiante =
          await obtenerDetalleExpediente(
            estudiante.id_estudiante,
            this.ciclo.id_ciclo
          );

      } catch (error) {
        console.error(error);

        this.detalleEstudiante = null;

        this.errorModal =
          error.response?.data?.mensaje ||
          "No fue posible cargar el expediente del estudiante.";
      }
    },


    seleccionarArchivoInstitucional(
      event
    ) {
      this.formInstitucional.archivo =
        event.target.files?.[0] || null;
    },


    seleccionarArchivoExpediente(
      event
    ) {
      this.formExpediente.archivo =
        event.target.files?.[0] || null;
    },


    validarArchivoFrontend(
      archivo
    ) {
      if (!archivo) {
        return "Seleccione un archivo.";
      }

      const extension =
        "." +
        archivo.name
          .split(".")
          .pop()
          .toLowerCase();

      const permitidas = [
        ".pdf",
        ".docx",
        ".xlsx",
        ".jpg",
        ".jpeg",
        ".png"
      ];

      if (
        !permitidas.includes(
          extension
        )
      ) {
        return (
          "Formato no permitido. " +
          "Use PDF, DOCX, XLSX, JPG, JPEG o PNG."
        );
      }

      if (
        archivo.size >
        10 * 1024 * 1024
      ) {
        return "El archivo supera los 10 MB.";
      }

      return null;
    },


    async guardarDocumento() {
      if (
        this.tipoDocumento ===
        "institucional"
      ) {
        await this.guardarInstitucional();
        return;
      }

      await this.guardarDocumentoExpediente();
    },


    async guardarInstitucional() {
      if (!this.formInstitucional.titulo) {
        this.errorModal =
          "Escriba el título del documento.";

        return;
      }

      if (
        !this.formInstitucional.id_categoria
      ) {
        this.errorModal =
          "Seleccione una categoría.";

        return;
      }

      if (
        !this.formInstitucional.nivel_acceso
      ) {
        this.errorModal =
          "Seleccione un nivel de acceso.";

        return;
      }

      if (
        !this.formInstitucional.fecha_documental
      ) {
        this.errorModal =
          "Seleccione la fecha documental.";

        return;
      }

      const errorArchivo =
        this.validarArchivoFrontend(
          this.formInstitucional.archivo
        );

      if (errorArchivo) {
        this.errorModal =
          errorArchivo;

        return;
      }

      this.procesando = true;
      this.errorModal = "";

      try {
        const respuesta =
          await subirDocumentoRepositorio({
            id_ciclo:
              this.ciclo.id_ciclo,

            id_categoria:
              Number(
                this.formInstitucional.id_categoria
              ),

            titulo:
              this.formInstitucional.titulo,

            descripcion:
              this.formInstitucional.descripcion,

            nivel_acceso:
              this.formInstitucional.nivel_acceso,

            fecha_documental:
              this.formInstitucional.fecha_documental,

            archivo:
              this.formInstitucional.archivo
          });

        this.mostrarToast(
          respuesta.mensaje
        );

        this.modalSubir = false;

        this.resetFormularioSubida();

        await this.cargarRepositorio();

      } catch (error) {
        console.error(error);

        this.errorModal =
          error.response?.data?.mensaje ||
          "No fue posible guardar el documento.";

      } finally {
        this.procesando = false;
      }
    },


    async guardarDocumentoExpediente() {
      if (
        !this.formExpediente.id_seccion
      ) {
        this.errorModal =
          "Seleccione grado y sección.";

        return;
      }

      if (
        !this.estudianteSeleccionado
      ) {
        this.errorModal =
          "Seleccione un estudiante.";

        return;
      }

      if (
        !this.formExpediente.id_requisito
      ) {
        this.errorModal =
          "Seleccione el documento del expediente.";

        return;
      }

      const errorArchivo =
        this.validarArchivoFrontend(
          this.formExpediente.archivo
        );

      if (errorArchivo) {
        this.errorModal =
          errorArchivo;

        return;
      }

      this.procesando = true;
      this.errorModal = "";

      try {
        const respuesta =
          await subirDocumento(
            this.estudianteSeleccionado
              .id_estudiante,
            {
              id_ciclo:
                this.ciclo.id_ciclo,

              id_requisito:
                Number(
                  this.formExpediente
                    .id_requisito
                ),

              observaciones:
                this.formExpediente
                  .observaciones,

              archivo:
                this.formExpediente.archivo
            }
          );

        this.mostrarToast(
          respuesta.mensaje
        );

        this.modalSubir = false;

        this.resetFormularioSubida();

        await this.cargarRepositorio();

      } catch (error) {
        console.error(error);

        this.errorModal =
          error.response?.data?.mensaje ||
          "No fue posible guardar el documento del expediente.";

      } finally {
        this.procesando = false;
      }
    },


    async abrirFicha(
      documento
    ) {
      this.modalFicha = true;
      this.cargandoDetalle = true;
      this.detalleDocumento = null;
      this.error = "";

      try {
        const data =
          await obtenerDetalleDocumentoRepositorio(
            documento.id_documento
          );

        this.detalleDocumento =
          data.documento;

      } catch (error) {
        console.error(error);

        this.error =
          error.response?.data?.mensaje ||
          "No fue posible abrir la ficha.";

        this.modalFicha = false;

      } finally {
        this.cargandoDetalle = false;
      }
    },


    cerrarFicha() {
      this.modalFicha = false;
      this.detalleDocumento = null;
    },


    abrirAdministrar(
      documento
    ) {
      this.documentoAdministrar =
        documento;

      this.modalAdministrar = true;
    },


    cerrarAdministrar() {
      this.modalAdministrar = false;
      this.documentoAdministrar = null;
    },


    async abrirFichaDesdeAdmin() {
      const documento =
        this.documentoAdministrar;

      this.modalAdministrar = false;

      if (documento) {
        await this.abrirFicha(
          documento
        );
      }
    },


    abrirEditarMetadatos() {
      if (!this.documentoAdministrar) {
        return;
      }

      this.errorModal = "";

      this.formEditar = {
        titulo:
          this.documentoAdministrar.titulo,

        id_categoria:
          this.documentoAdministrar.id_categoria,

        estado:
          this.documentoAdministrar.estado,

        nivel_acceso:
          this.documentoAdministrar.nivel_acceso,

        descripcion:
          this.documentoAdministrar.descripcion || ""
      };

      this.modalEditar = true;
    },


    cerrarEditar() {
      if (this.procesando) {
        return;
      }

      this.modalEditar = false;
      this.errorModal = "";
    },


    async guardarMetadatos() {
      if (!this.formEditar.titulo) {
        this.errorModal =
          "El título es obligatorio.";

        return;
      }

      this.procesando = true;
      this.errorModal = "";

      try {
        const respuesta =
          await actualizarDocumentoRepositorio(
            this.documentoAdministrar
              .id_documento,
            {
              titulo:
                this.formEditar.titulo,

              id_categoria:
                Number(
                  this.formEditar.id_categoria
                ),

              estado:
                this.formEditar.estado,

              nivel_acceso:
                this.formEditar.nivel_acceso,

              descripcion:
                this.formEditar.descripcion
            }
          );

        this.mostrarToast(
          respuesta.mensaje
        );

        this.modalEditar = false;
        this.modalAdministrar = false;

        this.documentoAdministrar =
          null;

        await this.cargarRepositorio();

      } catch (error) {
        console.error(error);

        this.errorModal =
          error.response?.data?.mensaje ||
          "No fue posible actualizar el documento.";

      } finally {
        this.procesando = false;
      }
    },


    abrirReemplazarArchivo() {
      this.formReemplazo = {
        archivo: null,
        motivo: ""
      };

      this.errorModal = "";
      this.modalReemplazar = true;
    },


    cerrarReemplazar() {
      if (this.procesando) {
        return;
      }

      this.modalReemplazar = false;
      this.errorModal = "";
    },


    seleccionarArchivoReemplazo(
      event
    ) {
      this.formReemplazo.archivo =
        event.target.files?.[0] || null;
    },


    async guardarReemplazo() {
      const errorArchivo =
        this.validarArchivoFrontend(
          this.formReemplazo.archivo
        );

      if (errorArchivo) {
        this.errorModal =
          errorArchivo;

        return;
      }

      if (!this.formReemplazo.motivo) {
        this.errorModal =
          "Indique el motivo del reemplazo.";

        return;
      }

      this.procesando = true;
      this.errorModal = "";

      try {
        const respuesta =
          await reemplazarArchivoRepositorio(
            this.documentoAdministrar
              .id_documento,
            {
              archivo:
                this.formReemplazo.archivo,

              motivo:
                this.formReemplazo.motivo
            }
          );

        this.mostrarToast(
          respuesta.mensaje
        );

        this.modalReemplazar = false;
        this.modalAdministrar = false;

        this.documentoAdministrar =
          null;

        await this.cargarRepositorio();

      } catch (error) {
        console.error(error);

        this.errorModal =
          error.response?.data?.mensaje ||
          "No fue posible reemplazar el archivo.";

      } finally {
        this.procesando = false;
      }
    },


    abrirConfirmarPapelera() {
      this.errorModal = "";
      this.modalPapelera = true;
    },


    cerrarConfirmarPapelera() {
      if (this.procesando) {
        return;
      }

      this.modalPapelera = false;
      this.errorModal = "";
    },


    async confirmarPapelera() {
      if (!this.documentoAdministrar) {
        return;
      }

      this.procesando = true;
      this.errorModal = "";

      try {
        const respuesta =
          await enviarDocumentoPapelera(
            this.documentoAdministrar
              .id_documento
          );

        this.mostrarToast(
          respuesta.mensaje
        );

        this.modalPapelera = false;
        this.modalAdministrar = false;

        this.documentoAdministrar =
          null;

        await this.cargarRepositorio();

      } catch (error) {
        console.error(error);

        this.errorModal =
          error.response?.data?.mensaje ||
          "No fue posible enviar el documento a la papelera.";

      } finally {
        this.procesando = false;
      }
    },


    puedePrevisualizar(
      tipoMime
    ) {
      return [
        "application/pdf",
        "image/jpeg",
        "image/png"
      ].includes(tipoMime);
    },


    async visualizarDocumentoActual() {
      if (!this.detalleDocumento) {
        return;
      }

      try {
        await verDocumentoRepositorio(
          this.detalleDocumento
            .id_documento
        );

      } catch (error) {
        console.error(error);

        this.error =
          error.response?.data?.mensaje ||
          "No fue posible abrir el archivo.";
      }
    },


    async descargarDocumentoActual() {
      if (!this.detalleDocumento) {
        return;
      }

      try {
        await descargarDocumentoRepositorio(
          this.detalleDocumento
            .id_documento
        );

      } catch (error) {
        console.error(error);

        this.error =
          "No fue posible descargar el archivo.";
      }
    },


    async descargarVersion(
      version
    ) {
      try {
        await descargarVersionRepositorio(
          version.id_version
        );

      } catch (error) {
        console.error(error);

        this.error =
          "No fue posible descargar esta versión.";
      }
    },


    formatearFecha(
      fecha
    ) {
      if (!fecha) {
        return "—";
      }

      const partes =
        String(fecha)
          .slice(0, 10)
          .split("-");

      if (partes.length !== 3) {
        return fecha;
      }

      return (
        `${partes[2]}/${partes[1]}/${partes[0]}`
      );
    },


    formatearFechaHora(
      fecha
    ) {
      if (!fecha) {
        return "—";
      }

      const valor =
        new Date(fecha);

      if (
        Number.isNaN(
          valor.getTime()
        )
      ) {
        return fecha;
      }

      return valor.toLocaleString(
        "es-GT",
        {
          dateStyle: "short",
          timeStyle: "short"
        }
      );
    },


    formatearTamano(
      bytes
    ) {
      const numero =
        Number(bytes || 0);

      if (!numero) {
        return "—";
      }

      if (numero < 1024) {
        return `${numero} B`;
      }

      if (
        numero <
        1024 * 1024
      ) {
        return (
          `${(numero / 1024).toFixed(1)} KB`
        );
      }

      return (
        `${(
          numero /
          (1024 * 1024)
        ).toFixed(2)} MB`
      );
    },


    obtenerFormato(
      nombre
    ) {
      if (!nombre) {
        return "—";
      }

      const partes =
        nombre.split(".");

      if (partes.length < 2) {
        return "—";
      }

      return partes
        .pop()
        .toUpperCase();
    }
  }
};
</script>