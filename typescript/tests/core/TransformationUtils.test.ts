/**
 * Unit tests for TransformationUtils.
 */

import { describe, it, expect } from 'vitest';
import { TransformationUtils } from '../../src/core/TransformationUtils';

describe('TransformationUtils', () => {
  describe('floatToMaxDecimalsString', () => {
    it('should format float with default decimals', () => {
      const result = TransformationUtils.floatToMaxDecimalsString(1.23456789);
      expect(result).toContain('1.23456789');
    });

    it('should format float with specified decimals', () => {
      const result = TransformationUtils.floatToMaxDecimalsString(1.23456789, 3);
      expect(result).toBe('1.235');
    });
  });

  describe('arrayToCSVString', () => {
    it('should convert transformation matrix to CSV', () => {
      const transform = {
        matrix: [
          [1, 0, 0, 0],
          [0, 1, 0, 0],
          [0, 0, 1, 0],
          [0, 0, 0, 1]
        ]
      };

      const result = TransformationUtils.arrayToCSVString(transform);
      const lines = result.split('\n');
      
      expect(lines).toHaveLength(4);
      expect(lines[0]).toContain('1');
    });
  });

  describe('createIdentity', () => {
    it('should create identity matrix', () => {
      const identity = TransformationUtils.createIdentity();
      
      expect(identity.matrix[0][0]).toBe(1);
      expect(identity.matrix[1][1]).toBe(1);
      expect(identity.matrix[2][2]).toBe(1);
      expect(identity.matrix[3][3]).toBe(1);
      expect(identity.matrix[0][3]).toBe(0);
    });
  });

  describe('multiply', () => {
    it('should multiply identity by identity', () => {
      const id1 = TransformationUtils.createIdentity();
      const id2 = TransformationUtils.createIdentity();
      const result = TransformationUtils.multiply(id1, id2);
      
      // Identity * Identity = Identity
      expect(result.matrix[0][0]).toBe(1);
      expect(result.matrix[1][1]).toBe(1);
      expect(result.matrix[2][2]).toBe(1);
      expect(result.matrix[3][3]).toBe(1);
      expect(result.matrix[0][3]).toBe(0);
      expect(result.matrix[1][3]).toBe(0);
      expect(result.matrix[2][3]).toBe(0);
    });

    it('should multiply translation matrices', () => {
      const t1 = {
        matrix: [
          [1, 0, 0, 1],
          [0, 1, 0, 0],
          [0, 0, 1, 0],
          [0, 0, 0, 1]
        ]
      };
      const t2 = {
        matrix: [
          [1, 0, 0, 1],
          [0, 1, 0, 0],
          [0, 0, 1, 0],
          [0, 0, 0, 1]
        ]
      };
      
      const result = TransformationUtils.multiply(t1, t2);
      expect(result.matrix[0][3]).toBe(2); // Combined translation
    });
  });

  describe('invert', () => {
    it('should invert identity matrix', () => {
      const identity = TransformationUtils.createIdentity();
      const inverted = TransformationUtils.invert(identity);
      
      // Check each element (handles -0 vs 0)
      for (let i = 0; i < 4; i++) {
        for (let j = 0; j < 4; j++) {
          expect(inverted.matrix[i][j]).toBeCloseTo(identity.matrix[i][j], 10);
        }
      }
    });

    it('should invert translation matrix', () => {
      const translation = {
        matrix: [
          [1, 0, 0, 1],
          [0, 1, 0, 1],
          [0, 0, 1, 1],
          [0, 0, 0, 1]
        ]
      };
      
      const inverted = TransformationUtils.invert(translation);
      expect(inverted.matrix[0][3]).toBeCloseTo(-1, 5);
      expect(inverted.matrix[1][3]).toBeCloseTo(-1, 5);
      expect(inverted.matrix[2][3]).toBeCloseTo(-1, 5);
    });
  });
});

