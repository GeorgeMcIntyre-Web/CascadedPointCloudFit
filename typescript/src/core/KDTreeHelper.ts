/**
 * KD-Tree helper for efficient nearest neighbor search.
 * 
 * Wraps kd-tree-javascript library for point cloud operations.
 */

import { Point3D, PointCloud } from './types';
import { PointCloudHelper } from './PointCloudHelper';

// Simple KD-Tree implementation for 3D points
export class KDTree3D {
  private points: Point3D[];
  private root: KDNode | null = null;

  constructor(points: Point3D[]) {
    this.points = points;
    this.root = this.buildTree(points, 0);
  }

  /**
   * Find nearest neighbor to a point.
   * 
   * @param point Query point
   * @returns Nearest point and distance
   */
  nearest(point: Point3D): { point: Point3D; distance: number } {
    if (!this.root || this.points.length === 0) {
      throw new Error('KD-Tree is empty');
    }

    let best: { point: Point3D; distance: number } | null = null;
    let bestDist = Infinity;

    this.search(this.root, point, 0, (node) => {
      const dist = this.distance(point, node.point);
      if (dist < bestDist) {
        bestDist = dist;
        best = { point: node.point, distance: dist };
      }
    });

    if (!best) {
      throw new Error('No nearest neighbor found');
    }

    return best;
  }

  /**
   * Find k nearest neighbors.
   * 
   * @param point Query point
   * @param k Number of neighbors
   * @returns Array of nearest points with distances
   */
  nearestK(point: Point3D, k: number): Array<{ point: Point3D; distance: number }> {
    if (!this.root || this.points.length === 0) {
      throw new Error('KD-Tree is empty');
    }

    const candidates: Array<{ point: Point3D; distance: number }> = [];

    this.search(this.root, point, 0, (node) => {
      const dist = this.distance(point, node.point);
      candidates.push({ point: node.point, distance: dist });
    });

    // Sort by distance and return k nearest
    candidates.sort((a, b) => a.distance - b.distance);
    return candidates.slice(0, Math.min(k, candidates.length));
  }

  /**
   * Query all points within a radius.
   * 
   * @param point Query point
   * @param radius Search radius
   * @returns Array of points within radius
   */
  withinRadius(point: Point3D, radius: number): Array<{ point: Point3D; distance: number }> {
    if (!this.root || this.points.length === 0) {
      return [];
    }

    const results: Array<{ point: Point3D; distance: number }> = [];
    const radiusSq = radius * radius;

    this.search(this.root, point, 0, (node) => {
      const distSq = this.distanceSquared(point, node.point);
      if (distSq <= radiusSq) {
        results.push({ point: node.point, distance: Math.sqrt(distSq) });
      }
    });

    return results;
  }

  private buildTree(points: Point3D[], depth: number): KDNode | null {
    if (points.length === 0) {
      return null;
    }

    if (points.length === 1) {
      return new KDNode(points[0]);
    }

    const axis = depth % 3; // 0=x, 1=y, 2=z
    const sorted = [...points].sort((a, b) => {
      const aVal = axis === 0 ? a.x : axis === 1 ? a.y : a.z;
      const bVal = axis === 0 ? b.x : axis === 1 ? b.y : b.z;
      return aVal - bVal;
    });

    const median = Math.floor(sorted.length / 2);
    const node = new KDNode(sorted[median]);

    node.left = this.buildTree(sorted.slice(0, median), depth + 1);
    node.right = this.buildTree(sorted.slice(median + 1), depth + 1);

    return node;
  }

  private search(
    node: KDNode | null,
    point: Point3D,
    depth: number,
    visit: (node: KDNode) => void
  ): void {
    if (!node) {
      return;
    }

    visit(node);

    const axis = depth % 3;
    const nodeVal = axis === 0 ? node.point.x : axis === 1 ? node.point.y : node.point.z;
    const pointVal = axis === 0 ? point.x : axis === 1 ? point.y : point.z;

    const diff = pointVal - nodeVal;
    const primary = diff < 0 ? node.left : node.right;
    const secondary = diff < 0 ? node.right : node.left;

    if (primary) {
      this.search(primary, point, depth + 1, visit);
    }

    // Check if we need to search the other side
    if (secondary && Math.abs(diff) < this.distance(point, node.point)) {
      this.search(secondary, point, depth + 1, visit);
    }
  }

  private distance(p1: Point3D, p2: Point3D): number {
    const dx = p1.x - p2.x;
    const dy = p1.y - p2.y;
    const dz = p1.z - p2.z;
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }

  private distanceSquared(p1: Point3D, p2: Point3D): number {
    const dx = p1.x - p2.x;
    const dy = p1.y - p2.y;
    const dz = p1.z - p2.z;
    return dx * dx + dy * dy + dz * dz;
  }
}

class KDNode {
  point: Point3D;
  left: KDNode | null = null;
  right: KDNode | null = null;

  constructor(point: Point3D) {
    this.point = point;
  }
}

/**
 * Create KD-Tree from point cloud.
 * 
 * @param cloud Point cloud
 * @returns KD-Tree instance
 */
export function createKDTree(cloud: PointCloud): KDTree3D {
  const points = PointCloudHelper.toPoints(cloud);
  return new KDTree3D(points);
}

