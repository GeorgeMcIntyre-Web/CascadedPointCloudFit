/**
 * Unit tests for RegistrationAlgorithms.
 */

import { describe, it, expect } from 'vitest';
import { RegistrationAlgorithms } from '../../src/core/RegistrationAlgorithms';
import { PointCloudHelper } from '../../src/core/PointCloudHelper';
import { PointCloud } from '../../src/core/types';

describe('RegistrationAlgorithms', () => {
  describe('pcaRegistration', () => {
    it('should compute transformation for simple translation', () => {
      // Create source and target with simple translation
      const sourcePoints = [
        { x: 0, y: 0, z: 0 },
        { x: 1, y: 0, z: 0 },
        { x: 0, y: 1, z: 0 },
        { x: 0, y: 0, z: 1 }
      ];
      
      const targetPoints = sourcePoints.map(p => ({
        x: p.x + 1,
        y: p.y + 1,
        z: p.z + 1
      }));
      
      const source = PointCloudHelper.fromPoints(sourcePoints);
      const target = PointCloudHelper.fromPoints(targetPoints);
      
      const transform = RegistrationAlgorithms.pcaRegistration(source, target);
      
      expect(transform.matrix).toHaveLength(4);
      expect(transform.matrix[0]).toHaveLength(4);
      expect(transform.matrix[3]).toEqual([0, 0, 0, 1]); // Bottom row
    });

    it('should handle minimum 3 points', () => {
      const sourcePoints = [
        { x: 0, y: 0, z: 0 },
        { x: 1, y: 0, z: 0 },
        { x: 0, y: 1, z: 0 }
      ];
      
      const targetPoints = [
        { x: 1, y: 1, z: 1 },
        { x: 2, y: 1, z: 1 },
        { x: 1, y: 2, z: 1 }
      ];
      
      const source = PointCloudHelper.fromPoints(sourcePoints);
      const target = PointCloudHelper.fromPoints(targetPoints);
      
      const transform = RegistrationAlgorithms.pcaRegistration(source, target);
      
      expect(transform.matrix).toBeDefined();
    });

    it('should throw error for insufficient points', () => {
      const sourcePoints = [
        { x: 0, y: 0, z: 0 },
        { x: 1, y: 0, z: 0 }
      ];
      
      const targetPoints = [
        { x: 1, y: 1, z: 1 },
        { x: 2, y: 1, z: 1 }
      ];
      
      const source = PointCloudHelper.fromPoints(sourcePoints);
      const target = PointCloudHelper.fromPoints(targetPoints);
      
      expect(() => {
        RegistrationAlgorithms.pcaRegistration(source, target);
      }).toThrow('at least 3 points');
    });
  });

  describe('icpRefinement', () => {
    it('should refine transformation', () => {
      const sourcePoints = [
        { x: 0, y: 0, z: 0 },
        { x: 1, y: 0, z: 0 },
        { x: 0, y: 1, z: 0 },
        { x: 0, y: 0, z: 1 }
      ];
      
      const targetPoints = sourcePoints.map(p => ({
        x: p.x + 0.1,
        y: p.y + 0.1,
        z: p.z + 0.1
      }));
      
      const source = PointCloudHelper.fromPoints(sourcePoints);
      const target = PointCloudHelper.fromPoints(targetPoints);
      
      // Initial transform (identity)
      const initialTransform = {
        matrix: [
          [1, 0, 0, 0],
          [0, 1, 0, 0],
          [0, 0, 1, 0],
          [0, 0, 0, 1]
        ]
      };
      
      const result = RegistrationAlgorithms.icpRefinement(
        source,
        target,
        initialTransform,
        10, // maxIterations
        1e-6 // tolerance
      );
      
      expect(result.transform).toBeDefined();
      expect(result.iterations).toBeGreaterThan(0);
      expect(result.iterations).toBeLessThanOrEqual(10);
      expect(result.error).toBeGreaterThanOrEqual(0);
    });

    it('should throw error for insufficient points', () => {
      const sourcePoints = [
        { x: 0, y: 0, z: 0 },
        { x: 1, y: 0, z: 0 }
      ];
      
      const targetPoints = [
        { x: 1, y: 1, z: 1 },
        { x: 2, y: 1, z: 1 }
      ];
      
      const source = PointCloudHelper.fromPoints(sourcePoints);
      const target = PointCloudHelper.fromPoints(targetPoints);
      
      const initialTransform = {
        matrix: [
          [1, 0, 0, 0],
          [0, 1, 0, 0],
          [0, 0, 1, 0],
          [0, 0, 0, 1]
        ]
      };
      
      expect(() => {
        RegistrationAlgorithms.icpRefinement(source, target, initialTransform);
      }).toThrow('at least 3 points');
    });
  });
});

