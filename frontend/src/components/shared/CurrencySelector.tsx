/**
 * CurrencySelector — Searchable dropdown for selecting any world currency.
 * Shows priority currencies (USD, INR, EUR, etc.) at top.
 * Search filters by code or name.
 * Used in: ResultsPage header, EstimatesPage header, NewEstimatePage.
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import {
  useCurrencyStore,
  PRIORITY_CURRENCY_CODES,
  CURRENCY_SYMBOLS,
  CURRENCY_NAMES,
} from '../../store/currencyStore';
import { ChevronDown } from 'lucide-react';

interface CurrencySelectorProps {
  compact?: boolean;
}

export default function CurrencySelector({ compact = false }: CurrencySelectorProps) {
  const { currency, setCurrency, rates, refreshRatesIfStale, ratesFetchedAt } = useCurrencyStore();
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);

  // Fetch fresh rates when selector opens
  useEffect(() => {
    if (open) {
      refreshRatesIfStale();
      // Focus search input when dropdown opens
      setTimeout(() => searchRef.current?.focus(), 50);
    }
  }, [open]);

  // Close on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpen(false);
        setSearch('');
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // Keyboard handling
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setOpen(false);
      setSearch('');
    }
  }, []);

  // Build list: priority currencies first, then all others alphabetically
  const allCodes = Object.keys(rates)
    .map((c) => c.toUpperCase())
    .filter((c) => c.length === 3);

  const prioritySet = new Set(PRIORITY_CURRENCY_CODES);
  const others = allCodes
    .filter((c) => !prioritySet.has(c))
    .sort();
  const allOrdered = [
    ...PRIORITY_CURRENCY_CODES.filter((c) => allCodes.includes(c)),
    ...others,
  ];

  const filtered = search.trim()
    ? allOrdered.filter((c) => {
        const q = search.toLowerCase();
        return (
          c.toLowerCase().includes(q) ||
          (CURRENCY_NAMES[c] ?? '').toLowerCase().includes(q) ||
          (CURRENCY_SYMBOLS[c] ?? '').toLowerCase().includes(q)
        );
      })
    : allOrdered;

  const handleSelect = useCallback(
    (code: string) => {
      setCurrency(code);
      setOpen(false);
      setSearch('');
    },
    [setCurrency]
  );

  const sym = CURRENCY_SYMBOLS[currency] ?? currency;
  const isLive = ratesFetchedAt > 0 && (Date.now() - ratesFetchedAt) < 3600000;

  return (
    <div
      className="currency-selector"
      ref={dropdownRef}
      onKeyDown={handleKeyDown}
    >
      <button
        className="currency-selector__trigger"
        onClick={() => setOpen(!open)}
        aria-label={`Currency: ${currency}. Click to change.`}
        aria-expanded={open}
        type="button"
      >
        <span className="currency-selector__symbol">{sym}</span>
        <span className="currency-selector__code">{currency}</span>
        {!compact && (
          <span className="currency-selector__name">
            {CURRENCY_NAMES[currency] ?? ''}
          </span>
        )}
        {isLive && <span className="currency-selector__live-dot" title="Live rates" />}
        <ChevronDown
          size={14}
          style={{
            transition: 'transform 0.2s',
            transform: open ? 'rotate(180deg)' : 'rotate(0)',
            opacity: 0.5,
          }}
        />
      </button>

      {open && (
        <div className="currency-selector__dropdown" role="listbox" aria-label="Select currency">
          <div className="currency-selector__search-wrap">
            <input
              ref={searchRef}
              className="currency-selector__search"
              type="text"
              placeholder="Search currency..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              aria-label="Search currencies"
            />
          </div>
          <div className="currency-selector__list">
            {filtered.length === 0 && (
              <div className="currency-selector__empty">No currencies found</div>
            )}
            {filtered.slice(0, 50).map((code) => (
              <button
                key={code}
                role="option"
                type="button"
                aria-selected={code === currency}
                className={`currency-selector__item ${
                  code === currency ? 'currency-selector__item--selected' : ''
                }`}
                onClick={() => handleSelect(code)}
              >
                <span className="currency-selector__item-symbol">
                  {CURRENCY_SYMBOLS[code] ?? code}
                </span>
                <span className="currency-selector__item-code">{code}</span>
                <span className="currency-selector__item-name">
                  {CURRENCY_NAMES[code] ?? ''}
                </span>
                {code === currency && (
                  <span style={{ marginLeft: 'auto', fontSize: '0.75rem', opacity: 0.6 }}>✓</span>
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
