import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, PlusCircle, FolderOpen, Settings, ChevronLeft, ChevronRight } from 'lucide-react';

const navItems = [
  { label: 'Dashboard', icon: LayoutDashboard, route: '/dashboard' },
  { label: 'New Estimate', icon: PlusCircle, route: '/estimate/new' },
  { label: 'My Estimates', icon: FolderOpen, route: '/estimates' },
  { label: 'Settings', icon: Settings, route: '/settings' },
];
interface SidebarProps { collapsed?: boolean; setCollapsed?: (value: boolean) => void; }

export default function Sidebar({ collapsed: controlled, setCollapsed: onChange }: SidebarProps) {
  const [internal, setInternal] = useState(false);
  const collapsed = controlled ?? internal;
  return (
    <nav aria-label="Workspace navigation" className={`workspace-nav${collapsed ? ' is-collapsed' : ''}`}>
      <div className="workspace-nav-links">
        {navItems.map(({ label, icon: Icon, route }) => (
          <NavLink key={route} to={route} end={route === '/estimate/new'}
            aria-label={label} title={collapsed ? label : undefined}
            className={({ isActive }) => `workspace-nav-link${isActive ? ' is-active' : ''}`}>
            <Icon size={20} aria-hidden="true" /><span>{label}</span>
          </NavLink>
        ))}
      </div>
      <button type="button" className="workspace-nav-toggle"
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'} aria-expanded={!collapsed}
        onClick={() => (onChange ?? setInternal)(!collapsed)}>
        {collapsed ? <ChevronRight size={20} aria-hidden="true" /> : <ChevronLeft size={20} aria-hidden="true" />}
        {!collapsed && <span>Collapse navigation</span>}
      </button>
    </nav>
  );
}
