import { beforeEach, describe, expect, it, vi } from 'vitest';
import { signInWithPopup, type UserCredential } from 'firebase/auth';
import { useAuthStore } from '../authStore';
import api from '@/lib/api';

vi.mock('@/lib/firebase', () => ({ auth: {} }));
vi.mock('@/lib/api', () => ({ default: { post: vi.fn(), get: vi.fn() } }));
vi.mock('firebase/auth', async (original) => ({
  ...await original<typeof import('firebase/auth')>(),
  signInWithPopup: vi.fn(),
}));

describe('social authentication', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    useAuthStore.setState({ loading: false, user: null, session: null });
  });

  it.each(['google', 'github'] as const)('signs in through %s and synchronizes the verified token', async (provider) => {
    const user = { getIdToken: vi.fn().mockResolvedValue('test-token'), displayName: 'Test User', photoURL: null };
    vi.mocked(signInWithPopup).mockResolvedValue({ user } as unknown as UserCredential);
    await useAuthStore.getState().signInWithOAuth(provider);
    expect(vi.mocked(signInWithPopup).mock.calls[0][1].providerId).toBe(`${provider}.com`);
    expect(api.post).toHaveBeenCalledWith('/auth/firebase', {}, { headers: { Authorization: 'Bearer test-token' } });
    expect(useAuthStore.getState()).toMatchObject({ loading: false, session: { user } });
  });

  it.each([
    ['auth/popup-blocked', 'Allow pop-ups for this site'],
    ['auth/popup-closed-by-user', 'Sign-in popup was closed'],
    ['auth/unauthorized-domain', 'predictiq-preview.vercel.app'],
    ['auth/operation-not-allowed', 'This sign-in method is not enabled'],
  ])('gives a useful message for %s and permits retry', async (code, message) => {
    vi.mocked(signInWithPopup).mockRejectedValue({ code });
    await expect(useAuthStore.getState().signInWithOAuth('google')).rejects.toThrow(message);
    expect(useAuthStore.getState()).toMatchObject({ loading: false, session: null });
    expect(api.post).not.toHaveBeenCalled();
  });

  it('does not let a second provider click cancel the active popup', async () => {
    let reject!: (reason: unknown) => void;
    vi.mocked(signInWithPopup).mockReturnValue(new Promise((_resolve, fail) => { reject = fail; }));
    const first = useAuthStore.getState().signInWithOAuth('google');
    expect(useAuthStore.getState().loading).toBe(true);
    await useAuthStore.getState().signInWithOAuth('github');
    expect(signInWithPopup).toHaveBeenCalledTimes(1);
    reject({ code: 'auth/popup-closed-by-user' });
    await expect(first).rejects.toThrow('closed');
    expect(useAuthStore.getState().loading).toBe(false);
  });
});
