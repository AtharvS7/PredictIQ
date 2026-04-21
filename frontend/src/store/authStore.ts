/**
 * PredictIQ — Auth Store (Firebase Auth)
 * Zustand store managing authentication state via Firebase.
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
}

const googleProvider = new GoogleAuthProvider();
const githubProvider = new GithubAuthProvider();

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  profile: null,
  loading: false,
  initialized: false,
  session: null,

  setProfile: (profile) => set({ profile }),

  initialize: async () => {
    return new Promise<void>((resolve) => {
      const unsubscribe = onAuthStateChanged(auth, async (user) => {
        set({
          user,
          session: user ? { user } : null,
          initialized: true,
        });

        if (user) {
          // Fetch profile from backend
          try {
            await get().fetchProfile();
          } catch {
            // Profile may not exist yet for new users
          }
        } else {
          set({ profile: null });
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
    } finally {
      set({ loading: false });
    }
  },

  signIn: async (email, password) => {
    set({ loading: true });
    try {
      const { user } = await signInWithEmailAndPassword(auth, email, password);
      set({
        user,
        session: { user },
      });
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
    set({ user: null, session: null, profile: null });
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
}));
