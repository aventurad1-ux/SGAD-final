import { createRouter, createWebHistory } from "vue-router";

import LoginView from "../views/auth/LoginView.vue";
import DashboardView from "../views/directora/DashboardView.vue";
import ReviewInboxView from "../views/directora/ReviewInboxView.vue";
import RequestsView from "../views/directora/RequestsView.vue";
import ExpedientesView from "../views/directora/ExpedientesView.vue";

const routes = [
  {
    path: "/",
    name: "login",
    component: LoginView
  },
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
  }

];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to) => {
  const accessToken = localStorage.getItem("access_token");
  const usuarioGuardado = localStorage.getItem("usuario");

  let usuario = null;

  if (usuarioGuardado) {
    try {
      usuario = JSON.parse(usuarioGuardado);
    } catch {
      usuario = null;
    }
  }

  if (to.meta.requiresAuth && !accessToken) {
    return "/";
  }

  if (
    to.meta.role &&
    (!usuario || usuario.rol !== to.meta.role)
  ) {
    return "/";
  }

  if (to.path === "/" && accessToken && usuario) {
    if (usuario.rol === "Directora") {
      return "/directora/dashboard";
    }
  }
});

export default router;
