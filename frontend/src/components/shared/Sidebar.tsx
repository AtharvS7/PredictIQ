import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, PlusCircle, FolderOpen, Settings, HelpCircle,
  ChevronLeft, ChevronRight,
} from 'lucide-react';
import { useState } from 'react';

const navItems = [
  { label: 'Dashboard', icon: LayoutDashboard, route: '/dashboard' },
  { label: 'New Estimate', icon: PlusCircle, route: '/estimate/new' },
  { label: 'My Estimates', icon: FolderOpen, route: '/estimates' },
  { label: 'Settings', icon: Settings, route: '/settings' },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  return (
    <aside style={{
      width: collapsed ? 68 : 240,
      minHeight: 'calc(100vh - 64px)',
      background: 'var(--bg-surface)',
      borderRight: '1px solid var(--border-color)',
      transition: 'width 0.25s var(--transition-smooth, ease)',
      display: 'flex', flexDirection: 'column',
      padding: '0.75rem 0',
      position: 'relative',
      flexShrink: 0,
    }}>
      {/* Subtle gradient tint at top */}
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, height: 80,
        background: 'var(--gradient-brand-subtle, transparent)',
        opacity: 0.5, pointerEvents: 'none', borderRadius: '0 0 20px 0',
      }} />

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 2, padding: '0 0.5rem', position: 'relative', zIndex: 1 }}>
        {navItems.map(({ label, icon: Icon, route }) => {
          const isActive = location.pathname === route ||
            (route === '/estimate/new' && location.pathname.startsWith('/estimate/'));

          return (
            <NavLink
              key={route}
              to={route}
              style={{
                display: 'flex', alignItems: 'center', gap: 12,
                padding: collapsed ? '10px 0' : '10px 12px',
                justifyContent: collapsed ? 'center' : 'flex-start',
                borderRadius: 10, textDecoration: 'none',
                color: isActive ? 'var(--color-primary)' : 'var(--text-secondary)',
                background: isActive ? 'rgba(26, 86, 219, 0.08)' : 'transparent',
                fontWeight: isActive ? 600 : 500,
                fontSize: '0.875rem',
                transition: 'all 0.2s ease',
                borderLeft: isActive ? '4px solid transparent' : '4px solid transparent',
                borderImage: isActive ? 'var(--gradient-brand) 1' : 'none',
                paddingLeft: isActive ? (collapsed ? 0 : 8) : (collapsed ? 0 : 12),
                position: 'relative',
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.background = 'var(--bg-elevated)';
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.background = 'transparent';
              }}
            >
              <Icon size={20} />
              {!collapsed && <span>{label}</span>}
            </NavLink>
          );
        })}
      </div>

      {/* Version badge */}
      {!collapsed && (
        <div style={{
          padding: '0 0.75rem', marginBottom: 40,
          textAlign: 'center',
        }}>
          <span style={{
            fontSize: '0.6875rem',
            fontWeight: 500,
            color: 'var(--text-tertiary)',
            background: 'var(--bg-elevated)',
            padding: '3px 10px',
            borderRadius: 9999,
            letterSpacing: '0.02em',
          }}>
            PredictIQ v2.3
          </span>
        </div>
      )}

      <button
        onClick={() => setCollapsed(!collapsed)}
        style={{
          position: 'absolute', bottom: 16, right: collapsed ? 'calc(50% - 12px)' : 12,
          width: 24, height: 24, borderRadius: '50%',
          border: '1px solid var(--border-color)', background: 'var(--bg-surface)',
          cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: 'var(--text-secondary)', transition: 'all 0.2s',
        }}
      >
        {collapsed ? <ChevronRight size={13} /> : <ChevronLeft size={13} />}
      </button>
    </aside>
  );
}
