/**
 * Predictify — Currency Store Unit Tests
 * Tests for the Zustand currency store: conversion, formatting, symbols.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useCurrencyStore, CURRENCY_SYMBOLS, PRIORITY_CURRENCY_CODES } from '../currencyStore';

describe('CurrencyStore', () => {
  beforeEach(() => {
    // Reset store to defaults before each test
    useCurrencyStore.setState({
      currency: 'USD',
      rates: { usd: 1.0, inr: 84.5, eur: 0.92, gbp: 0.79, jpy: 152.0 },
      ratesFetchedAt: 0,
      loading: false,
      error: null,
    });
  });

  // ── setCurrency ──────────────────────────────────────────

  describe('setCurrency', () => {
    it('should set currency to uppercase', () => {
      useCurrencyStore.getState().setCurrency('inr');
      expect(useCurrencyStore.getState().currency).toBe('INR');
    });

    it('should accept already-uppercase codes', () => {
      useCurrencyStore.getState().setCurrency('EUR');
      expect(useCurrencyStore.getState().currency).toBe('EUR');
    });
  });

  // ── convert ──────────────────────────────────────────────

  describe('convert', () => {
    it('should return same amount for USD', () => {
      const result = useCurrencyStore.getState().convert(100);
      expect(result).toBe(100);
    });

    it('should convert USD to INR correctly', () => {
      useCurrencyStore.getState().setCurrency('INR');
      const result = useCurrencyStore.getState().convert(100);
      expect(result).toBe(8450);
    });

    it('should convert USD to EUR correctly', () => {
      useCurrencyStore.getState().setCurrency('EUR');
      const result = useCurrencyStore.getState().convert(100);
      expect(result).toBe(92);
    });

    it('should return 1x for unknown currency', () => {
      useCurrencyStore.getState().setCurrency('XYZ');
      const result = useCurrencyStore.getState().convert(100);
      expect(result).toBe(100); // fallback rate = 1.0
    });

    it('should handle zero amount', () => {
      useCurrencyStore.getState().setCurrency('INR');
      expect(useCurrencyStore.getState().convert(0)).toBe(0);
    });
  });

  // ── format ───────────────────────────────────────────────

  describe('format', () => {
    it('should format USD with dollar sign', () => {
      const result = useCurrencyStore.getState().format(1000);
      expect(result).toContain('$');
      expect(result).toContain('1,000');
    });

    it('should format INR with lakhs notation', () => {
      useCurrencyStore.getState().setCurrency('INR');
      const result = useCurrencyStore.getState().format(5000);
      // 5000 USD * 84.5 = 422,500 INR → ₹4.23L
      expect(result).toContain('₹');
      expect(result).toContain('L');
    });

    it('should format INR with crores for large amounts', () => {
      useCurrencyStore.getState().setCurrency('INR');
      const result = useCurrencyStore.getState().format(500000);
      // 500,000 USD * 84.5 = 42,250,000 INR → ₹4.23Cr
      expect(result).toContain('Cr');
    });

    it('should format JPY without decimal places', () => {
      useCurrencyStore.getState().setCurrency('JPY');
      const result = useCurrencyStore.getState().format(100);
      expect(result).toContain('¥');
      // Should not have decimal point
      expect(result).not.toContain('.');
    });
  });

  // ── symbol ───────────────────────────────────────────────

  describe('symbol', () => {
    it('should return $ for USD', () => {
      expect(useCurrencyStore.getState().symbol()).toBe('$');
    });

    it('should return ₹ for INR', () => {
      useCurrencyStore.getState().setCurrency('INR');
      expect(useCurrencyStore.getState().symbol()).toBe('₹');
    });

    it('should return code for unknown currency', () => {
      useCurrencyStore.getState().setCurrency('XYZ');
      expect(useCurrencyStore.getState().symbol()).toBe('XYZ');
    });
  });

  // ── getRate ──────────────────────────────────────────────

  describe('getRate', () => {
    it('should return 1.0 for USD', () => {
      expect(useCurrencyStore.getState().getRate()).toBe(1.0);
    });

    it('should return INR rate', () => {
      useCurrencyStore.getState().setCurrency('INR');
      expect(useCurrencyStore.getState().getRate()).toBe(84.5);
    });

    it('should return 1.0 for unknown currency', () => {
      useCurrencyStore.getState().setCurrency('XYZ');
      expect(useCurrencyStore.getState().getRate()).toBe(1.0);
    });
  });

  // ── Constants ────────────────────────────────────────────

  describe('constants', () => {
    it('should have USD in priority currencies', () => {
      expect(PRIORITY_CURRENCY_CODES).toContain('USD');
    });

    it('should have INR in priority currencies', () => {
      expect(PRIORITY_CURRENCY_CODES).toContain('INR');
    });

    it('should have symbols for all priority currencies', () => {
      for (const code of PRIORITY_CURRENCY_CODES) {
        expect(CURRENCY_SYMBOLS[code]).toBeDefined();
      }
    });
  });
});
