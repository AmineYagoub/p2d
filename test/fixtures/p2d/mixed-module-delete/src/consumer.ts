import { runFeature } from "./feature";
import type { FeatureConfig } from "./feature";

const config: FeatureConfig = { enabled: true };

export function consume() {
  return config.enabled ? runFeature() : "disabled";
}
