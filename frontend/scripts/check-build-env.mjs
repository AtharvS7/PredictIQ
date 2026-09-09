import { loadEnv } from 'vite';

const env = loadEnv('production', process.cwd(), 'VITE_');
const required = [
  'VITE_FIREBASE_API_KEY', 'VITE_FIREBASE_AUTH_DOMAIN', 'VITE_FIREBASE_PROJECT_ID',
  'VITE_FIREBASE_STORAGE_BUCKET', 'VITE_FIREBASE_MESSAGING_SENDER_ID', 'VITE_FIREBASE_APP_ID',
];
const missing = required.filter(name => !env[name]?.trim());
if (missing.length) {
  console.error(`Missing public Firebase build configuration: ${missing.join(', ')}`);
  process.exit(1);
}
