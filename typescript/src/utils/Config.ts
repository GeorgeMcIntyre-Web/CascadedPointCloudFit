/**
 * Configuration management.
 * 
 * Ported from Python: cascaded_fit/utils/config.py
 */

import * as fs from 'fs/promises';
import * as path from 'path';
import * as yaml from 'js-yaml';

export interface ICPConfig {
  maxCorrespondenceDistance: number;
  relativeFitness: number;
  relativeRmse: number;
}

export interface FGRConfig {
  distanceThreshold: number;
  voxelSize: number;
  maxCorrespondenceDistance: number;
  radiusNormalFactor?: number;
  radiusFeatureFactor?: number;
  maxNnNormal?: number;
  maxNnFeature?: number;
}

export interface RegistrationConfig {
  rmseThreshold: number;
  maxIterations: number;
  tolerance: number;
}

export interface APIConfig {
  host: string;
  port: number;
  debug: boolean;
  maxPoints: number;
  timeout: number;
  rmseThreshold: number;
  enableBidirectional: boolean;
}

export interface ConfigData {
  registration: RegistrationConfig;
  icp: ICPConfig;
  fgr: FGRConfig;
  api: APIConfig;
}

export class Config {
  private static instance: Config | null = null;
  private config: ConfigData | null = null;

  private constructor() {}

  static getInstance(): Config {
    if (!Config.instance) {
      Config.instance = new Config();
    }
    return Config.instance;
  }

  /**
   * Load configuration from YAML file.
   * 
   * @param configPath Optional path to config file. Defaults to config/default.yaml
   */
  async load(configPath?: string): Promise<void> {
    if (!configPath) {
      // Default to config/default.yaml in project root
      const projectRoot = path.resolve(__dirname, '../../..');
      configPath = path.join(projectRoot, 'config', 'default.yaml');
    }

    try {
      const content = await fs.readFile(configPath, 'utf-8');
      const parsed = yaml.load(content) as ConfigData;
      
      // Validate required sections
      this.validateConfig(parsed);
      
      this.config = parsed;
    } catch (error) {
      throw new Error(`Failed to load configuration: ${error}`);
    }
  }

  /**
   * Get configuration value by dot-separated key.
   * 
   * @param key Dot-separated key (e.g., 'registration.rmse_threshold')
   * @param defaultValue Default value if key not found
   */
  get(key: string, defaultValue?: any): any {
    if (!this.config) {
      throw new Error('Configuration not loaded. Call load() first.');
    }

    const keys = key.split('.');
    let value: any = this.config;

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        return defaultValue;
      }
    }

    return value !== undefined ? value : defaultValue;
  }

  /**
   * Get registration configuration.
   */
  getRegistrationConfig(): RegistrationConfig {
    if (!this.config) {
      throw new Error('Configuration not loaded. Call load() first.');
    }
    return this.config.registration;
  }

  /**
   * Get ICP configuration.
   */
  getICPConfig(): ICPConfig {
    if (!this.config) {
      throw new Error('Configuration not loaded. Call load() first.');
    }
    return this.config.icp;
  }

  /**
   * Get FGR configuration.
   */
  getFGRConfig(): FGRConfig {
    if (!this.config) {
      throw new Error('Configuration not loaded. Call load() first.');
    }
    return this.config.fgr;
  }

  /**
   * Get API configuration.
   */
  getAPIConfig(): APIConfig {
    if (!this.config) {
      throw new Error('Configuration not loaded. Call load() first.');
    }
    return this.config.api;
  }

  private validateConfig(config: any): void {
    const requiredSections = ['registration', 'icp', 'fgr', 'api'];
    const missing = requiredSections.filter(section => !(section in config));
    
    if (missing.length > 0) {
      throw new Error(`Configuration missing required sections: ${missing.join(', ')}`);
    }
  }
}

