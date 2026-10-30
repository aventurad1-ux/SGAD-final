
import {
  createRouter,
  createWebHistory
} from "vue-router";

import LoginView
  from "../views/auth/LoginView.vue";

import DashboardView
  from "../views/directora/DashboardView.vue";

import ReviewInboxView
  from "../views/directora/ReviewInboxView.vue";

import RequestsView
  from "../views/directora/RequestsView.vue";

import ExpedientesView
  from "../views/directora/ExpedientesView.vue";

import CicloEscolarView
  from "../views/directora/CicloEscolarView.vue";

import UsuariosPermisosView
  from "../views/directora/UsuariosPermisosView.vue";

import RepositoryView 
  from "../views/directora/RepositoryView.vue";

import TrashView 
  from "../views/directora/TrashView.vue";

import PerfilDirectoraView
  from "../views/directora/PerfilDirectoraView.vue";

import ReportsView
  from "../views/directora/ReportsView.vue";

import BackupView
  from "../views/directora/BackupView.vue";
  
import SegundoFactorView
  from "../views/auth/SegundoFactorView.vue";
/*
 * PERFIL DOCENTE
 */
import TeacherDashboardView
  from "../views/docente/TeacherDashboardView.vue";

import TeacherStudentsView
  from "../views/docente/TeacherStudentsView.vue";

import TeacherRequestsView
  from "../views/docente/TeacherRequestsView.vue";

import TeacherDocumentsView
  from "../views/docente/TeacherDocumentsView.vue";

import TeacherCorrectionsView
  from "../views/docente/TeacherCorrectionsView.vue";

import TeacherReceiptsView
  from "../views/docente/TeacherReceiptsView.vue";

import TeacherProfileView
  from "../views/docente/TeacherProfileView.vue";


const routes = [
  // =====================================================
  // LOGIN
  // =====================================================

  {
    path: "/",
    name: "login",
    component: LoginView
  },

  {
  path: "/verificacion-2fa",
  name: "verificacion-2fa",
  component: SegundoFactorView
},

  // =====================================================
  // DIRECTORA
  // =====================================================

  {
    path: "/directora/dashboard",
    name: "directora-dashboard",
    component: DashboardView,
    meta: {
      requiresAuth: true,
      role: "Directora"
    }
  },

  {
    path: "/directora/revision",
    name: "directora-revision",
    component: ReviewInboxView,
    meta: {
      requiresAuth: true,
      role: "Directora"
    }
  },

  {
    path: "/directora/solicitudes",
    name: "directora-solicitudes",
    component: RequestsView,
    meta: {
      requiresAuth: true,
      role: "Directora"
    }
  },

  {
    path: "/directora/expedientes",
    name: "directora-expedientes",
    component: ExpedientesView,
    meta: {
      requiresAuth: true,
      role: "Directora"
    }
  },

  {
    path: "/directora/ciclo-escolar",
    name: "directora-ciclo-escolar",
    component: CicloEscolarView,
    meta: {
      requiresAuth: true,
      role: "Directora"
    }
  },

  {
    path: "/directora/usuarios",
    name: "directora-usuarios",
    component: UsuariosPermisosView,
    meta: {
      requiresAuth: true,
      role: "Directora"
    }
  },
  {
    path: "/directora/repositorio",
    name: "directora-repositorio",
    component: RepositoryView,
    meta: {
      requiresAuth: true,
      role: "Directora"
    }
  },
  {
    path: "/directora/papelera",
    name: "directora-papelera",
    component: TrashView,
    meta: {
      requiresAuth: true,
      role: "Directora"
    }
  },

  
   {
    path: "/directora/perfil",
    name: "directora-perfil",
    component: PerfilDirectoraView,
    meta: {
      requiresAuth: true,
      role: "Directora"
    }
  },

  {
    path: "/directora/reportes",
    name: "directora-reportes",
    component: ReportsView,
    meta: {
      requiresAuth: true,
      role: "Directora"
    }
  },

  {
    path: "/directora/respaldos",
    name: "directora-respaldos",
    component: BackupView,
    meta: {
      requiresAuth: true,
      role: "Directora"
    }
 },

  // =====================================================
  // BITÁCORA - DIRECTORA
  // =====================================================

  {
    path: "/directora/bitacora",
    name: "directora-bitacora",
    component: () =>
      import("../views/directora/BitacoraView.vue"),
    meta: {
      requiresAuth: true,
      role: "Directora"
    }
  },

  // =====================================================
  // DOCENTE
  // =====================================================

  {
    path: "/docente/dashboard",
    name: "docente-dashboard",
    component: TeacherDashboardView,
    meta: {
      requiresAuth: true,
      role: "Docente"
    }
  },

  {
    path: "/docente/estudiantes",
    name: "docente-estudiantes",
    component: TeacherStudentsView,
    meta: {
      requiresAuth: true,
      role: "Docente"
    }
  },

  {
    path: "/docente/solicitudes",
    name: "docente-solicitudes",
    component: TeacherRequestsView,
    meta: {
      requiresAuth: true,
      role: "Docente"
    }
  },

  {
    path: "/docente/documentos",
    name: "docente-documentos",
    component: TeacherDocumentsView,
    meta: {
      requiresAuth: true,
      role: "Docente"
    }
  },

  {
    path: "/docente/correcciones",
    name: "docente-correcciones",
    component: TeacherCorrectionsView,
    meta: {
      requiresAuth: true,
      role: "Docente"
    }
  },

  {
    path: "/docente/comprobantes",
    name: "docente-comprobantes",
    component: TeacherReceiptsView,
    meta: {
      requiresAuth: true,
      role: "Docente"
    }
  },

  {
    path: "/docente/perfil",
    name: "docente-perfil",
    component: TeacherProfileView,
    meta: {
      requiresAuth: true,
      role: "Docente"
    }
  },

  // =====================================================
  // RUTA NO ENCONTRADA
  // =====================================================

  {
    path: "/:pathMatch(.*)*",
    redirect: "/"
  }

];


const router = createRouter({
  history: createWebHistory(),
  routes
});


router.beforeEach((to) => {
  const accessToken =
    localStorage.getItem(
      "access_token"
    );

  const usuarioGuardado =
    localStorage.getItem(
      "usuario"
    );

  let usuario = null;

  if (usuarioGuardado) {
    try {
      usuario =
        JSON.parse(
          usuarioGuardado
        );
    } catch {
      usuario = null;
    }
  }

  // =====================================================
  // RUTA PROTEGIDA SIN SESIÓN
  // =====================================================

  if (
    to.meta.requiresAuth &&
    (!accessToken || !usuario)
  ) {
    return "/";
  }

  // =====================================================
  // VALIDAR ROL
  // =====================================================

  if (
    to.meta.role &&
    usuario?.rol !==
      to.meta.role
  ) {
    if (
      usuario?.rol ===
      "Directora"
    ) {
      return "/directora/dashboard";
    }

    if (
      usuario?.rol ===
      "Docente"
    ) {
      return "/docente/dashboard";
    }

    return "/";
  }

  // =====================================================
  // USUARIO AUTENTICADO INTENTA VOLVER AL LOGIN
  // =====================================================

  if (
    to.path === "/" &&
    accessToken &&
    usuario
  ) {
    if (
      usuario.rol ===
      "Directora"
    ) {
      return "/directora/dashboard";
    }

    if (
      usuario.rol ===
      "Docente"
    ) {
      return "/docente/dashboard";
    }
  }
});


export default router;
