/**
 * Predictify Currency Store v2
 * ============================
 * Fetches live exchange rates from backend (/api/v1/currencies/rates).
 * Supports ALL currencies available from the exchange API (200+).
 * Caches rates in localStorage for 1 hour to avoid repeated fetches.
 * Falls back to hardcoded rates if backend is unreachable.
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';
const CACHE_TTL_MS = 60 * 60 * 1000; // 1 hour

// Currencies shown prominently in the selector (order matters)
export const PRIORITY_CURRENCY_CODES = [
  'USD', 'INR', 'EUR', 'GBP', 'AED', 'SGD', 'CAD', 'AUD',
  'JPY', 'CHF', 'CNY', 'HKD', 'MXN', 'BRL', 'KRW', 'NZD',
];

export const CURRENCY_SYMBOLS: Record<string, string> = {
  USD: '$', INR: '₹', EUR: '€', GBP: '£', JPY: '¥', CNY: '¥',
  AED: 'AED', SGD: 'S$', CAD: 'CA$', AUD: 'A$', CHF: 'Fr',
  HKD: 'HK$', MXN: '$', BRL: 'R$', KRW: '₩', NZD: 'NZ$',
  SEK: 'kr', NOK: 'kr', DKK: 'kr', ZAR: 'R',
};

export const CURRENCY_NAMES: Record<string, string> = {
  USD: 'US Dollar', INR: 'Indian Rupee', EUR: 'Euro', GBP: 'British Pound',
  JPY: 'Japanese Yen', CNY: 'Chinese Yuan', AED: 'UAE Dirham',
  SGD: 'Singapore Dollar', CAD: 'Canadian Dollar', AUD: 'Australian Dollar',
  CHF: 'Swiss Franc', HKD: 'Hong Kong Dollar', MXN: 'Mexican Peso',
  BRL: 'Brazilian Real', KRW: 'South Korean Won', NZD: 'New Zealand Dollar',
  SEK: 'Swedish Krona', NOK: 'Norwegian Krone', DKK: 'Danish Krone',
  ZAR: 'South African Rand',
};

// Emergency fallback rates (only used if backend is unreachable)
const FALLBACK_RATES: Record<string, number> = {
  usd: 1.0, inr: 84.5, eur: 0.92, gbp: 0.79, jpy: 152.0,
  aed: 3.67, sgd: 1.34, cad: 1.36, aud: 1.53, chf: 0.90,
  cny: 7.24, hkd: 7.82, mxn: 17.15, brl: 5.05, krw: 1330.0,
  nzd: 1.63, sek: 10.5, nok: 10.6, dkk: 6.9, zar: 18.5,
};

interface CurrencyState {
  /** Selected display currency code (e.g., 'USD', 'INR', 'EUR') */
  currency: string;
  /** Exchange rates from USD (key: lowercase code, value: rate) */
  rates: Record<string, number>;
  /** Timestamp when rates were last fetched */
  ratesFetchedAt: number;
  /** Whether rates are currently being fetched */
  loading: boolean;
  /** Error message if last fetch failed */
  error: string | null;

  // Actions
  setCurrency: (code: string) => void;
  fetchRates: () => Promise<void>;
  refreshRatesIfStale: () => Promise<void>;

  // Helpers
  convert: (usdAmount: number) => number;
  format: (usdAmount: number) => string;
  symbol: () => string;
  getRate: () => number;
}

export const useCurrencyStore = create<CurrencyState>()(
  persist(
    (set, get) => ({
      currency: 'USD',
      rates: FALLBACK_RATES,
      ratesFetchedAt: 0,
      loading: false,
      error: null,

      setCurrency: (code: string) => {
        const upper = code.toUpperCase();
        set({ currency: upper });
      },

      fetchRates: async () => {
        if (get().loading) return;
        set({ loading: true, error: null });
        try {
          const resp = await axios.get(`${API_BASE}/currencies/rates`, {
            timeout: 8000,
          });
          const { rates } = resp.data;
          if (rates && Object.keys(rates).length > 10) {
            set({
              rates: { usd: 1.0, ...rates },
              ratesFetchedAt: Date.now(),
              loading: false,
              error: null,
            });
          } else {
            throw new Error('Invalid rates response');
          }
        } catch (err: any) {
          set({
            loading: false,
            error: err.message ?? 'Failed to fetch exchange rates',
          });
          // Keep existing rates (don't reset to fallback — use what we have)
        }
      },

      refreshRatesIfStale: async () => {
        const { ratesFetchedAt, fetchRates } = get();
        const ageMs = Date.now() - ratesFetchedAt;
        if (ageMs > CACHE_TTL_MS) {
          await fetchRates();
        }
      },

      convert: (usdAmount: number): number => {
        const { currency, rates } = get();
        if (currency === 'USD') return usdAmount;
        const rate = rates[currency.toLowerCase()] ?? 1.0;
        return usdAmount * rate;
      },

      format: (usdAmount: number): string => {
        const { currency } = get();
        const converted = get().convert(usdAmount);
        const sym = CURRENCY_SYMBOLS[currency] ?? currency + ' ';

        if (currency === 'INR') {
          // Indian numbering: lakhs and crores
          if (converted >= 10_000_000) {
            return `₹${(converted / 10_000_000).toFixed(2)}Cr`;
          } else if (converted >= 100_000) {
            return `₹${(converted / 100_000).toFixed(2)}L`;
          } else {
            return `₹${converted.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
          }
        } else if (currency === 'JPY' || currency === 'KRW') {
          // Yen and Won have no decimal places
          return `${sym}${Math.round(converted).toLocaleString()}`;
        } else {
          return `${sym}${converted.toLocaleString('en-US', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
          })}`;
        }
      },

      symbol: (): string => {
        const { currency } = get();
        return CURRENCY_SYMBOLS[currency] ?? currency;
      },

      getRate: (): number => {
        const { currency, rates } = get();
        if (currency === 'USD') return 1.0;
        return rates[currency.toLowerCase()] ?? 1.0;
      },
    }),
    {
      name: 'Predictify-currency-v2',
      storage: createJSONStorage(() => localStorage),
      // Only persist currency selection, not the rates (re-fetch on load)
      partialize: (state) => ({ currency: state.currency }),
    }
  )
);
