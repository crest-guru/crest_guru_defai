import express from "express";
import { registerRoutes } from "./routes";
import { setupVite, serveStatic, log } from "./vite";
import cors from 'cors';
import dotenv from 'dotenv';
import http from 'http';
import path from 'path';


dotenv.config({ 
  path: path.resolve(process.cwd(), '.env.local')
});

const app = express();
const server = http.createServer(app);


const PORT = process.env.PORT || 5011;        
const API_URL = process.env.VITE_API_URL;     
const FRONTEND_URL = process.env.VITE_FRONTEND_URL;


const corsOptions = {
  origin: [FRONTEND_URL],
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Accept'],
  credentials: true
};


app.use(cors(corsOptions));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

app.options('*', cors(corsOptions));

// Маршруты
registerRoutes(app);

if (process.env.NODE_ENV === 'development') {
  await setupVite(app, server);
} else {
  serveStatic(app);
}


server.listen(PORT, "0.0.0.0", () => {
  log(`Frontend server running on port ${PORT}`);
  log(`API URL: ${API_URL}`);
});
