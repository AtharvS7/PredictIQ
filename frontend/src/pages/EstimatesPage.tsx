import { useTheme } from '@/components/ThemeProvider';
import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '@/components/shared/Navbar';
import Sidebar from '@/components/shared/Sidebar';
import SEOHead from '@/components/shared/SEOHead';
import CurrencySelector from '@/components/shared/CurrencySelector';
import { useEstimateStore } from '@/store/estimateStore';
import { useCurrencyStore } from '@/store/currencyStore';
import { useToast } from '@/App';
import {
  Search,
  Trash2,
  Copy,
  FolderOpen,
  PlusCircle,
} from 'lucide-react';
import { duplicateEstimate } from '@/lib/api';

const PROJECT_TYPES = [
  'Web App',
  'Mobile App',
  'API/Backend',
  'ML/AI System',
  'Data Platform',
  'Enterprise Software',
];

export default function EstimatesPage() {
  const {
    estimates,
    totalEstimates,
    loading,
    error,
    page,
    perPage,
    sort,
    filterType,
    fetchEstimates,
    removeEstimate,
    setPage,
    setSort,
    setFilterType,
  } = useEstimateStore();

  const { format } = useCurrencyStore();
  const { addToast } = useToast();
  const navigate = useNavigate();
  const [search, setSearch] = useState('');

  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme === 'dark';

  useEffect(() => {
    fetchEstimates();
    useCurrencyStore.getState().refreshRatesIfStale();
  }, [fetchEstimates, page, sort, filterType]);

  const filtered = search
    ? estimates.filter(
      (e) =>
        e.project_name
          .toLowerCase()
          .includes(search.toLowerCase()) ||
        e.project_type
          .toLowerCase()
          .includes(search.toLowerCase())
    )
    : estimates;

  const handleDuplicate = async (
    id: string,
    e: React.MouseEvent
  ) => {
    e.stopPropagation();
    try {
      await duplicateEstimate(id);
      addToast('success', 'Estimate duplicated');
      fetchEstimates();
    } catch {
      addToast('error', 'Duplication failed');
    }
  };

  const handleDelete = async (
    id: string,
    e: React.MouseEvent
  ) => {
    e.stopPropagation();
    if (!confirm('Delete this estimate?')) return;
    try {
      await removeEstimate(id);
      if (estimates.length === 1 && page > 1) setPage(page - 1);
      addToast('info', 'Estimate deleted');
    } catch {
      addToast('error', 'Failed to delete estimate. Please try again.');
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'var(--bg-primary)',
      }}
    >
      <SEOHead title="My Estimates" description="Browse, search, and manage all your software project cost estimates." />
      <Navbar />

      <div style={{ display: 'flex' }}>
        <Sidebar />

        <main
          role="main"
          aria-label="Estimates list"
          style={{
            flex: 1,
            padding: 'clamp(1rem, 3vw, 2rem)',
            minWidth: 0,
            maxWidth: 1100,
          }}
        >
          {/* Header */}

          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: 12,
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 24,
            }}
          >
            <div>
              <h1
                style={{
                  fontSize: '1.5rem',
                  fontWeight: 700,
                  color: 'var(--text-primary)',
                }}
              >
                My Estimates
              </h1>

              <p
                style={{
                  fontSize: '0.8125rem',
                  color: 'var(--text-secondary)',
                }}
              >
                {totalEstimates} total estimates
              </p>
            </div>

            <div
              style={{
                display: 'flex',
                gap: 12,
                alignItems: 'center',
              }}
            >
              <CurrencySelector compact />

              {/* THEME BUTTON */}

              <button
                onClick={() =>
                  navigate('/estimate/new')
                }
                style={{
                  padding: '10px 18px',
                  borderRadius: 8,

                  background: isDark
                    ? 'black'
                    : 'white',

                  color: isDark
                    ? 'white'
                    : 'black',

                  border: isDark
                    ? '1px solid white'
                    : '1px solid black',

                  cursor: 'pointer',

                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,

                  transition: 'all 0.2s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background =
                    isDark ? 'white' : 'black';
                  e.currentTarget.style.color =
                    isDark ? 'black' : 'white';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background =
                    isDark ? 'black' : 'white';
                  e.currentTarget.style.color =
                    isDark ? 'white' : 'black';
                }}
              >
                <PlusCircle size={16} />
                New Estimate
              </button>
            </div>
          </div>

          {/* Filters */}

          <div
            className="card"
            style={{
              padding: 16,
              marginBottom: 20,
              display: 'flex',
              gap: 12,
              alignItems: 'center',
              flexWrap: 'wrap',
            }}
          >
            <div
              style={{
                position: 'relative',
                flex: 1,
                minWidth: 200,
              }}
            >
              <Search
                size={16}
                style={{
                  position: 'absolute',
                  left: 12,
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'var(--text-tertiary)',
                }}
              />

              <input
                className="input-field"
                style={{ paddingLeft: 36 }}
                placeholder="Search this page..."
                aria-label="Search estimates on this page"
                value={search}
                onChange={(e) =>
                  setSearch(e.target.value)
                }
              />
            </div>

            <select
              className="input-field"
              style={{ width: 180 }}
              aria-label="Filter by project type"
              value={filterType || ''}
              onChange={(e) =>
                setFilterType(
                  e.target.value || null
                )
              }
            >
              <option value="">
                All Types
              </option>

              {PROJECT_TYPES.map((t) => (
                <option key={t}>{t}</option>
              ))}
            </select>

            <select
              className="input-field"
              style={{ width: 180 }}
              aria-label="Sort estimates"
              value={sort}
              onChange={(e) =>
                setSort(e.target.value)
              }
            >
              <option value="created_at_desc">
                Newest First
              </option>

              <option value="created_at_asc">
                Oldest First
              </option>

              <option value="cost_desc">
                Highest Cost
              </option>

              <option value="cost_asc">
                Lowest Cost
              </option>

              <option value="risk_desc">
                Highest Risk
              </option>
            </select>
          </div>

          {/* Table */}

          {error && (
            <div className="card" role="alert" style={{ padding: 24 }}>
              <p>We couldn't complete that request. Please try again.</p>
              <button className="btn-secondary" onClick={() => fetchEstimates()} disabled={loading}>Retry</button>
            </div>
          )}
          {loading ? (
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: 8,
              }}
            >
              {Array.from(
                { length: 5 },
                (_, i) => (
                  <div
                    key={i}
                    className="skeleton"
                    style={{
                      height: 64,
                      borderRadius: 12,
                    }}
                  />
                )
              )}
            </div>
          ) : error && estimates.length === 0 ? null : filtered.length === 0 ? (
            <div
              className="card"
              style={{
                padding: 64,
                textAlign: 'center',
              }}
            >
              <FolderOpen
                size={48}
                color="var(--text-tertiary)"
                style={{ opacity: 0.5 }}
              />

              <h3
                style={{
                  marginTop: 16,
                  fontWeight: 600,
                  color: 'var(--text-primary)',
                }}
              >
                No estimates found
              </h3>

              <p
                style={{
                  color: 'var(--text-secondary)',
                  fontSize: '0.875rem',
                  marginTop: 4,
                }}
              >
                {search
                  ? 'Try a different search term.'
                  : 'Create your first estimate to get started.'}
              </p>
            </div>
          ) : (
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: 8,
              }}
            >
              {filtered.map((est) => (
                <div
                  key={est.id}
                  className="card"
                  style={{
                    padding: '16px 20px',
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: 16,
                    alignItems: 'center',
                    justifyContent:
                      'space-between',
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 8,
                      }}
                    >
                      <Link
                        to={`/estimate/${est.id}/results`}
                        style={{
                          fontWeight: 600,
                          fontSize: '0.9375rem',
                          color:
                            'var(--text-primary)',
                        }}
                      >
                        {est.project_name}
                      </Link>

                      <span
                        style={{
                          fontSize: '0.6875rem',
                          padding: '2px 8px',
                          borderRadius: 6,
                          background:
                            'var(--bg-elevated)',
                          color:
                            'var(--text-secondary)',
                        }}
                      >
                        v{est.version}
                      </span>
                    </div>

                    <p
                      style={{
                        fontSize: '0.75rem',
                        color:
                          'var(--text-tertiary)',
                        marginTop: 2,
                      }}
                    >
                      {est.project_type} •{' '}
                      {new Date(
                        est.created_at
                      ).toLocaleDateString()}
                    </p>
                  </div>

                  <div
                    style={{
                      display: 'flex',
                      flexWrap: 'wrap',
                      alignItems: 'center',
                      gap: 16,
                    }}
                  >
                    <div
                      style={{
                        textAlign: 'right',
                      }}
                    >
                      <p
                        style={{
                          fontWeight: 600,
                          color:
                            'var(--color-primary)',
                        }}
                      >
                        {format(
                          est.cost_likely_usd ??
                          0
                        )}
                      </p>

                      <p
                        style={{
                          fontSize: '0.6875rem',
                          color:
                            'var(--text-tertiary)',
                        }}
                      >
                        {format(
                          est.cost_min_usd ??
                          0
                        )}{' '}
                        –{' '}
                        {format(
                          est.cost_max_usd ??
                          0
                        )}
                      </p>
                    </div>

                    {/* RISK BADGE — UNCHANGED */}

                    <div
                      style={{
                        textAlign: 'center',
                        minWidth: 60,
                      }}
                    >
                      <span
                        className={`risk-badge risk-${est.risk_level?.toLowerCase()}`}
                      >
                        {est.risk_level}
                      </span>
                    </div>

                    <div
                      style={{
                        display: 'flex',
                        gap: 4,
                      }}
                    >
                      <button
                        onClick={(e) =>
                          handleDuplicate(est.id, e)
                        }
                        style={{
                          width: 44,
                          height: 44,
                          borderRadius: 8,
                          border:
                            '1px solid var(--border-color)',
                          background:
                            'transparent',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems:
                            'center',
                          justifyContent:
                            'center',
                          color:
                            'var(--text-secondary)',
                        }}
                        title="Duplicate"
                        aria-label={`Duplicate ${est.project_name}`}
                      >
                        <Copy size={14} />
                      </button>

                      <button
                        onClick={(e) =>
                          handleDelete(
                            est.id,
                            e
                          )
                        }
                        style={{
                          width: 44,
                          height: 44,
                          borderRadius: 8,
                          border:
                            '1px solid var(--border-color)',
                          background:
                            'transparent',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems:
                            'center',
                          justifyContent:
                            'center',
                          color:
                            'var(--color-danger)',
                        }}
                        title="Delete"
                        aria-label={`Delete ${est.project_name}`}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
          {totalEstimates > perPage && (
            <nav aria-label="Estimates pagination" style={{ display: 'flex', gap: 16, alignItems: 'center', justifyContent: 'center', flexWrap: 'wrap', marginTop: 24 }}>
              <button className="btn-secondary" disabled={loading || page <= 1} onClick={() => setPage(page - 1)}>Previous page</button>
              <span aria-live="polite">Page {page} of {Math.max(1, Math.ceil(totalEstimates / perPage))}</span>
              <button className="btn-secondary" disabled={loading || page * perPage >= totalEstimates} onClick={() => setPage(page + 1)}>Next page</button>
            </nav>
          )}
        </main>
      </div>
    </div>
  );
}
