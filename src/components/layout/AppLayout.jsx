import React, { useEffect } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import AppSidebar from "./AppSidebar";

export default function AppLayout() {
  const navigate = useNavigate();

  useEffect(() => {
    const role = localStorage.getItem("role");

    if (!role) {
      navigate("/login");
    }
  }, [navigate]);

  return (
    <div className="min-h-screen bg-background">
      <AppSidebar />
      <main className="ml-16 min-h-screen">
        <Outlet />
      </main>
    </div>
  );
}