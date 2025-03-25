import express, { type Request, Response, NextFunction } from "express";
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
const NODE_ENV = process.env.NODE_ENV || 'development';
const DEV_URL = process.env.VITE_API_URL || 'http://localhost:5010';
const PROD_URL = process.env.VITE_API_URL || 'http://localhost:5010';

const corsOptions = {
  origin: true, 
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Accept', 'Origin', 'X-Requested-With', 'Access-Control-Request-Method', 'Access-Control-Request-Headers', 'Access-Control-Allow-Origin', 'Access-Control-Allow-Credentials'],
  credentials: false 
};


app.use(cors(corsOptions));


app.use(express.json());
app.use(express.urlencoded({ extended: false }));

app.use((req, res, next) => {
  const start = Date.now();
  const path = req.path;
  let capturedJsonResponse: Record<string, any> | undefined = undefined;

  const originalResJson = res.json;
  res.json = function (bodyJson, ...args) {
    capturedJsonResponse = bodyJson;
    return originalResJson.apply(res, [bodyJson, ...args]);
  };

  res.on("finish", () => {
    const duration = Date.now() - start;
    if (path.startsWith("/api")) {
      let logLine = `${req.method} ${path} ${res.statusCode} in ${duration}ms`;
      if (capturedJsonResponse) {
        logLine += ` :: ${JSON.stringify(capturedJsonResponse)}`;
      }

      if (logLine.length > 80) {
        logLine = logLine.slice(0, 79) + "…";
      }

      log(logLine);
    }
  });

  next();
});

registerRoutes(app);

if (NODE_ENV === 'development') {
  await setupVite(app, server);
} else {
  serveStatic(app);
}

server.listen(PORT, "0.0.0.0", () => {
  log(`Server running in ${NODE_ENV} mode on port ${PORT}`);
  log(`API URL: ${NODE_ENV === 'development' ? DEV_URL : PROD_URL}`);
});
