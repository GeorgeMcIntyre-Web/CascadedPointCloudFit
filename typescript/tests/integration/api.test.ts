/**
 * Integration tests for REST API.
 */

import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { createApp, startServer } from '../../src/api/server';
import * as http from 'http';

describe('Integration: REST API', () => {
  let server: http.Server | null = null;
  const port = 5001; // Use different port to avoid conflicts

  beforeAll(async () => {
    const app = await createApp();
    server = app.listen(port, () => {
      console.log(`Test server listening on port ${port}`);
    });
    
    // Wait for server to be ready
    await new Promise(resolve => setTimeout(resolve, 100));
  });

  afterAll(async () => {
    if (server) {
      await new Promise<void>((resolve) => {
        server!.close(() => resolve());
      });
    }
  });

  describe('Health Endpoint', () => {
    it('should return healthy status', async () => {
      const response = await fetch(`http://localhost:${port}/health`);
      expect(response.status).toBe(200);
      
      const data = await response.json();
      expect(data.status).toBe('healthy');
      expect(data.service).toBe('point-cloud-registration-api');
    });
  });

  describe('Registration Endpoint', () => {
    it('should process valid point clouds', async () => {
      const requestBody = {
        sourcePoints: new Float64Array([0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1]),
        targetPoints: new Float64Array([1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2]),
        options: {
          rmseThreshold: 0.1,
          maxIterations: 50,
          tolerance: 1e-7
        }
      };

      const response = await fetch(`http://localhost:${port}/process_point_clouds`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          sourcePoints: Array.from(requestBody.sourcePoints),
          targetPoints: Array.from(requestBody.targetPoints),
          options: requestBody.options
        })
      });

      expect(response.status).toBe(200);
      
      const data = await response.json();
      expect(data).toHaveProperty('transformation');
      expect(data).toHaveProperty('inlier_rmse');
      expect(data).toHaveProperty('is_success');
      expect(data).toHaveProperty('metrics');
      expect(Array.isArray(data.transformation)).toBe(true);
      expect(data.transformation).toHaveLength(4);
    });

    it('should return error for missing data', async () => {
      const response = await fetch(`http://localhost:${port}/process_point_clouds`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      });

      expect(response.status).toBe(400);
      
      const data = await response.json();
      expect(data).toHaveProperty('error');
    });

    it('should return error for insufficient points', async () => {
      const response = await fetch(`http://localhost:${port}/process_point_clouds`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          sourcePoints: [0, 0, 0],
          targetPoints: [1, 1, 1]
        })
      });

      expect(response.status).toBe(400);
    });
  });
});

