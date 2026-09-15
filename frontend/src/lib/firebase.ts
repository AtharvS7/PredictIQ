/**
 * Predictify — Firebase Client Initialization
 * Replaces the former Supabase client.
 */
import { initializeApp } from 'firebase/app';
import { connectAuthEmulator, getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
// Explicit development-only emulator mode, restricted to a non-live project.
if (import.meta.env.DEV && import.meta.env.VITE_AUTH_EMULATOR === 'true') {
  if (firebaseConfig.projectId !== 'demo-predictiq') throw new Error('Auth emulator requires demo-predictiq');
  connectAuthEmulator(auth, 'http://127.0.0.1:9099');
}
export default app;
