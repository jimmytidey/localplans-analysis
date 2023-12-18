import { defineConfig,loadEnv } from 'vite'
import path from "path";
import react from '@vitejs/plugin-react'


// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  // Load app-level env vars to node-level env vars.
  process.env = {...process.env, ...loadEnv(mode, process.cwd())};


  return defineConfig({
    build: {
      outDir: '../app'
    }
  });
  }
)




