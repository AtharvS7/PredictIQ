/**
 * Predictify — Auth Store (Firebase Auth + RBAC)
 * Zustand store managing authentication state via Firebase.
 * Extracts role from Firebase custom claims for RBAC enforcement.
 */
import { create } from 'zustand';
import { auth } from '@/lib/firebase';
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  updateProfile,
  GoogleAuthProvider,
  GithubAuthProvider,
  sendPasswordResetEmail,
  type User,
} from 'firebase/auth';
import type { UserProfile } from '@/types';
import api from '@/lib/api';

interface AuthState {
  user: User | null;
  profile: UserProfile | null;
  loading: boolean;
  initialized: boolean;
  /** User's RBAC role extracted from Firebase custom claims */
  role: 'admin' | 'editor' | 'viewer';
  /** Convenience getter — true when user is signed in */
  session: { user: User } | null;
  setProfile: (profile: UserProfile | null) => void;
  initialize: () => Promise<void>;
  signUp: (email: string, password: string, fullName: string) => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signInWithOAuth: (provider: 'google' | 'github') => Promise<void>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  fetchProfile: () => Promise<void>;
  updateProfile: (data: Partial<UserProfile>) => Promise<void>;
  /** Check if user has at least the given role */
  hasRole: (minimumRole: 'admin' | 'editor' | 'viewer') => boolean;
}

const googleProvider = new GoogleAuthProvider();
const githubProvider = new GithubAuthProvider();

/**
 * Maps raw Firebase error codes to user-friendly messages.
 * Firebase v9+ merged user-not-found and wrong-password into
 * a single 'auth/invalid-credential' code for security.
 */
function mapFirebaseError(error: any): Error {
  const code = error?.code || '';
  const messages: Record<string, string> = {
    'auth/invalid-credential': 'Invalid email or password. Please check your credentials or sign up first.',
    'auth/user-not-found': 'No account found with this email. Please sign up first.',
    'auth/wrong-password': 'Incorrect password. Please try again.',
    'auth/email-already-in-use': 'An account with this email already exists. Try signing in instead.',
    'auth/weak-password': 'Password is too weak. Use at least 6 characters.',
    'auth/invalid-email': 'Please enter a valid email address.',
    'auth/too-many-requests': 'Too many failed attempts. Please wait a moment and try again.',
    'auth/network-request-failed': 'Network error. Please check your connection.',
    'auth/operation-not-allowed': 'Email/password sign-in is not enabled. Contact support.',
    'auth/popup-closed-by-user': 'Sign-in popup was closed.',
    'auth/unauthorized-domain': 'This domain is not authorized. Add it in the Firebase console.',
    'auth/account-exists-with-different-credential': 'An account already exists with this email using a different sign-in method (e.g., Google or GitHub).',
  };
  return new Error(messages[code] || error?.message || 'Authentication failed. Please try again.');
}

const ROLE_LEVELS: Record<string, number> = { viewer: 1, editor: 2, admin: 3 };

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  profile: null,
  loading: false,
  initialized: false,
  role: 'editor',
  session: null,

  setProfile: (profile) => set({ profile }),

  initialize: async () => {
    return new Promise<void>((resolve) => {
      const unsubscribe = onAuthStateChanged(auth, async (user) => {
        if (user) {
          // Extract role from Firebase custom claims
          const tokenResult = await user.getIdTokenResult();
          const role = (tokenResult.claims.role as string) || 'editor';
          const validRole = ['admin', 'editor', 'viewer'].includes(role)
            ? (role as 'admin' | 'editor' | 'viewer')
            : 'editor';

          set({
            user,
            role: validRole,
            session: { user },
            initialized: true,
          });

          // Fetch profile from backend
          try {
            await get().fetchProfile();
          } catch {
            // Profile may not exist yet for new users
          }
        } else {
          set({
            user: null,
            role: 'editor',
            session: null,
            profile: null,
            initialized: true,
          });
        }

        resolve();
      });

      // Store unsubscribe for cleanup if needed
      (window as any).__authUnsubscribe = unsubscribe;
    });
  },

  signUp: async (email, password, fullName) => {
    set({ loading: true });
    try {
      const { user } = await createUserWithEmailAndPassword(auth, email, password);

      // Set display name in Firebase
      await updateProfile(user, { displayName: fullName });

      // Get fresh ID token
      const token = await user.getIdToken();

      // Sync user with backend (verify + create DB record)
      try {
        await api.post(
          '/auth/firebase',
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } catch {
        // Non-critical — backend may not have /auth/firebase endpoint yet
      }

      // Create profile in backend
      try {
        await api.post('/profile', { full_name: fullName });
      } catch {
        // Non-critical — profile will be created on first fetch
      }

      set({
        user,
        session: { user },
      });
    } catch (error: any) {
      throw mapFirebaseError(error);
    } finally {
      set({ loading: false });
    }
  },

  signIn: async (email, password) => {
    set({ loading: true });
    try {
      const { user } = await signInWithEmailAndPassword(auth, email, password);

      // Sync token with backend
      const token = await user.getIdToken();
      try {
        await api.post(
          '/auth/firebase',
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } catch {
        // Non-critical
      }

      set({
        user,
        session: { user },
      });
    } catch (error: any) {
      throw mapFirebaseError(error);
    } finally {
      set({ loading: false });
    }
  },

  signInWithOAuth: async (provider) => {
    const authProvider = provider === 'google' ? googleProvider : githubProvider;

    try {
      const { user } = await signInWithPopup(auth, authProvider);

      // Step 1: Get Firebase ID Token
      const token = await user.getIdToken();

      // Step 2: Send token to backend — verifies + syncs user in DB
      await api.post(
        '/auth/firebase',
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      // Step 3: Set session locally
      set({
        user,
        session: { user },
      });

      // Step 4: Create/update profile (now authenticated)
      try {
        await api.post('/profile', {
          full_name: user.displayName || '',
          avatar_url: user.photoURL || '',
        });
      } catch {
        // Non-critical
      }
    } catch (error: any) {
      if (error?.code === 'auth/popup-closed-by-user') {
        throw new Error('Sign-in popup was closed');
      }
      if (error?.code === 'auth/unauthorized-domain') {
        throw new Error('Add domain in Firebase console');
      }
      throw error;
    }
  },

  signOut: async () => {
    await firebaseSignOut(auth);
    set({ user: null, session: null, profile: null, role: 'editor' });
  },

  resetPassword: async (email) => {
    await sendPasswordResetEmail(auth, email);
  },

  fetchProfile: async () => {
    const user = get().user;
    if (!user) return;

    try {
      const { data } = await api.get('/profile');
      set({ profile: data });
    } catch {
      // Profile doesn't exist — create a default one
      try {
        const { data } = await api.post('/profile', {
          full_name: user.displayName || '',
          avatar_url: user.photoURL || '',
        });
        set({ profile: data });
      } catch {
        console.error('Could not create profile');
      }
    }
  },

  updateProfile: async (updates) => {
    const user = get().user;
    if (!user) return;

    try {
      const { data } = await api.patch('/profile', updates);
      set({ profile: data });
    } catch (error) {
      console.error('Update profile error:', error);
      throw error;
    }
  },

  hasRole: (minimumRole) => {
    const userLevel = ROLE_LEVELS[get().role] ?? 0;
    const requiredLevel = ROLE_LEVELS[minimumRole] ?? 0;
    return userLevel >= requiredLevel;
  },
}));
