import { useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  PlusCircle,
  FolderOpen,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

const navItems = [
  { label: "Dashboard", icon: LayoutDashboard, route: "/dashboard" },
  { label: "New Estimate", icon: PlusCircle, route: "/estimate/new" },
  { label: "My Estimates", icon: FolderOpen, route: "/estimates" },
  { label: "Settings", icon: Settings, route: "/settings" },
];

interface SidebarProps {
  collapsed?: boolean;
  setCollapsed?: (val: boolean) => void;
}

export default function Sidebar({ collapsed: controlledCollapsed, setCollapsed: controlledSetCollapsed }: SidebarProps) {
  const [internalCollapsed, setInternalCollapsed] = useState(false);
  const collapsed = controlledCollapsed ?? internalCollapsed;
  const setCollapsed = controlledSetCollapsed ?? setInternalCollapsed;
  const location = useLocation();

  const textColor = "var(--text-primary)";
  const borderColor = "var(--text-primary)";

  return (
    <aside
      role="navigation"
      aria-label="Sidebar navigation"
      style={{
        width: collapsed ? 68 : 240,
        minHeight: "100vh",
        background: "var(--bg-surface)",
        borderRight: `1px solid ${borderColor}`,
        transition: "width 0.25s ease",
        display: "flex",
        flexDirection: "column",
        padding: "0.75rem 0",
        position: "relative",
      }}
    >
      {/* Navigation */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          gap: 2,
          padding: "0 0.5rem",
        }}
      >
        {navItems.map(({ label, icon: Icon, route }) => {
          const isActive =
            location.pathname === route ||
            (route === "/estimate/new" &&
              location.pathname.startsWith("/estimate/"));

          return (
            <NavLink
              key={route}
              to={route}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                padding: collapsed ? "10px 0" : "10px 12px",
                justifyContent: collapsed ? "center" : "flex-start",
                borderRadius: 10,
                textDecoration: "none",

                color: textColor,

                background: isActive
                  ? "rgba(0,0,0,0.08)"
                  : "transparent",

                fontWeight: isActive ? 700 : 500,
                fontSize: "0.875rem",
                transition: "all 0.2s ease",
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background =
                    "rgba(0,0,0,0.05)";
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background =
                    "transparent";
                }
              }}
            >
              <Icon size={20} color={textColor} />

              {!collapsed && <span>{label}</span>}
            </NavLink>
          );
        })}
      </div>

      {/* Version */}
      {!collapsed && (
        <div
          style={{
            padding: "0 0.75rem",
            marginBottom: 40,
            textAlign: "center",
          }}
        >
          <span
            style={{
              fontSize: "0.6875rem",
              fontWeight: 500,
              color: textColor,
            }}
          >
            Predictify v2.3
          </span>
        </div>
      )}

      {/* Toggle Button */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        title={collapsed ? "Expand Sidebar" : "Collapse Sidebar"}
        aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        aria-expanded={!collapsed}
        style={{
          position: "absolute",
          top: 16,
          right: -14,

          width: 28,
          height: 28,

          display: "flex",
          alignItems: "center",
          justifyContent: "center",

          borderRadius: "50%",
          border: `1px solid ${borderColor}`,
          background: "var(--bg-surface)",

          cursor: "pointer",
          color: textColor,

          transition: "all 0.2s ease",
          zIndex: 1000,
        }}
      >
        {collapsed ? (
          <ChevronRight size={16} />
        ) : (
          <ChevronLeft size={16} />
        )}
      </button>
    </aside>
  );
}