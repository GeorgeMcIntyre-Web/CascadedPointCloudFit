/**
 * Unit tests for KDTreeHelper.
 */

import { describe, it, expect } from 'vitest';
import { createKDTree, KDTree3D } from '../../src/core/KDTreeHelper';
import { PointCloudHelper } from '../../src/core/PointCloudHelper';

describe('KDTreeHelper', () => {
  describe('KDTree3D', () => {
    it('should find nearest neighbor', () => {
      const points = [
        { x: 0, y: 0, z: 0 },
        { x: 1, y: 0, z: 0 },
        { x: 0, y: 1, z: 0 },
        { x: 0, y: 0, z: 1 },
        { x: 5, y: 5, z: 5 }
      ];

      const tree = new KDTree3D(points);
      const nearest = tree.nearest({ x: 0.1, y: 0.1, z: 0.1 });

      expect(nearest.point).toEqual({ x: 0, y: 0, z: 0 });
      expect(nearest.distance).toBeCloseTo(Math.sqrt(0.03), 5);
    });

    it('should find k nearest neighbors', () => {
      const points = [
        { x: 0, y: 0, z: 0 },
        { x: 1, y: 0, z: 0 },
        { x: 0, y: 1, z: 0 },
        { x: 0, y: 0, z: 1 },
        { x: 5, y: 5, z: 5 }
      ];

      const tree = new KDTree3D(points);
      const nearest3 = tree.nearestK({ x: 0.1, y: 0.1, z: 0.1 }, 3);

      expect(nearest3).toHaveLength(3);
      expect(nearest3[0].point).toEqual({ x: 0, y: 0, z: 0 });
    });

    it('should find points within radius', () => {
      const points = [
        { x: 0, y: 0, z: 0 },
        { x: 1, y: 0, z: 0 },
        { x: 0, y: 1, z: 0 },
        { x: 5, y: 5, z: 5 }
      ];

      const tree = new KDTree3D(points);
      const within = tree.withinRadius({ x: 0.1, y: 0.1, z: 0.1 }, 1.5);

      expect(within.length).toBeGreaterThanOrEqual(3);
      expect(within.every(r => r.distance <= 1.5)).toBe(true);
    });
  });

  describe('createKDTree', () => {
    it('should create KD-Tree from point cloud', () => {
      const points = [
        { x: 0, y: 0, z: 0 },
        { x: 1, y: 0, z: 0 },
        { x: 0, y: 1, z: 0 }
      ];

      const cloud = PointCloudHelper.fromPoints(points);
      const tree = createKDTree(cloud);

      const nearest = tree.nearest({ x: 0.5, y: 0.5, z: 0 });
      expect(nearest.point).toBeDefined();
      expect(nearest.distance).toBeGreaterThanOrEqual(0);
    });
  });
});

