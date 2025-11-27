/**
 * REST API server for point cloud registration.
 * 
 * Ported from Python: cascaded_fit/api/app.py
 */

import express, { Request, Response } from 'express';
import { PointCloudReader } from '../io/PointCloudReader';
import { RegistrationAlgorithms } from '../core/RegistrationAlgorithms';
import { MetricsCalculator } from '../core/MetricsCalculator';
import { PointCloudHelper } from '../core/PointCloudHelper';
import { Config } from '../utils/Config';

const app = express();
app.use(express.json({ limit: '100mb' })); // Large point clouds

// Health check endpoint
app.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    service: 'point-cloud-registration-api'
  });
});

// Main registration endpoint
app.post('/process_point_clouds', async (req: Request, res: Response) => {
  try {
    const { sourcePoints, targetPoints, options } = req.body;

    if (!sourcePoints || !targetPoints) {
      return res.status(400).json({
        error: 'Missing required fields: sourcePoints and targetPoints'
      });
    }

    // Convert arrays to point clouds
    const sourceCloud = PointCloudHelper.fromFlatArray(sourcePoints);
    const targetCloud = PointCloudHelper.fromFlatArray(targetPoints);

    // Validate point counts
    if (sourceCloud.count < 3 || targetCloud.count < 3) {
      return res.status(400).json({
        error: 'Point clouds must have at least 3 points each'
      });
    }

    // Align cloud sizes
    const [alignedSource, alignedTarget] = PointCloudReader.alignCloudSizes(
      sourceCloud,
      targetCloud
    );

    // Get configuration
    const rmseThreshold = options?.rmseThreshold || 0.01;
    const maxIterations = options?.maxIterations || 200;
    const tolerance = options?.tolerance || 1e-7;

    // Run PCA registration
    const initialTransform = RegistrationAlgorithms.pcaRegistration(
      alignedSource,
      alignedTarget
    );

    // Run ICP refinement
    const icpResult = RegistrationAlgorithms.icpRefinement(
      alignedSource,
      alignedTarget,
      initialTransform,
      maxIterations,
      tolerance
    );

    // Compute metrics
    const metrics = MetricsCalculator.computeMetrics(
      alignedSource,
      alignedTarget,
      icpResult.transform
    );

    // Determine success
    const isSuccess = metrics.rmse < rmseThreshold;

    res.json({
      transformation: icpResult.transform.matrix,
      inlier_rmse: metrics.rmse,
      max_error: metrics.maxError,
      is_success: isSuccess,
      method: 'Custom ICP',
      metrics: {
        rmse: metrics.rmse,
        maxError: metrics.maxError,
        meanError: metrics.meanError,
        medianError: metrics.medianError
      }
    });
  } catch (error: any) {
    console.error('Registration error:', error);
    res.status(500).json({
      error: error.message || 'Internal server error'
    });
  }
});

/**
 * Create and configure Express app.
 * 
 * @param configPath Optional path to configuration file
 * @returns Configured Express app
 */
export async function createApp(configPath?: string): Promise<express.Application> {
  if (configPath) {
    const config = Config.getInstance();
    await config.load(configPath);
  }

  return app;
}

/**
 * Start the API server.
 * 
 * @param port Server port (default: 5000)
 * @param host Server host (default: '0.0.0.0')
 */
export async function startServer(port: number = 5000, host: string = '0.0.0.0'): Promise<void> {
  const server = app.listen(port, host, () => {
    console.log(`Point Cloud Registration API listening on ${host}:${port}`);
  });

  // Graceful shutdown
  process.on('SIGTERM', () => {
    server.close(() => {
      console.log('Server closed');
      process.exit(0);
    });
  });
}

// Start server if run directly
if (require.main === module) {
  startServer().catch(console.error);
}

export default app;

