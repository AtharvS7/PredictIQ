import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://tkfdwkxfahmxezzzccmz.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRrZmR3a3hmYWhteGV6enpjY216Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU2NDIyNTcsImV4cCI6MjA5MTIxODI1N30.Yu75DSfOScMPP87DTWnRs8oV749Y56rU9sYXH8EeK24';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
