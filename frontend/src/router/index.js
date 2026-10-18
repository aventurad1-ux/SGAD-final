import { createRouter, createWebHistory } from "vue-router";

import LoginView from "../views/auth/LoginView.vue";
import DashboardView from "../views/directora/DashboardView.vue";

const routes = [
  {
    path: "/",
    name: "login",
    component: LoginView
  },
  {
    path: "/directora/dashboard",
    name: "directora-dashboard",
    component: DashboardView
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
