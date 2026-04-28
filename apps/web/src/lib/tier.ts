/**
 * Tier helpers — single source of truth for "is this feature available
 * to a user on this tenant on this tier?".
 *
 * The shape of `tier_features` mirrors tenants/base/config.json. Each
 * tier may inherit from the previous one by listing its name as the
 * first entry, e.g. `pro: ["start", "audit_vk", ...]`.
 */

export type Tier = "start" | "pro" | "expert";

export interface TenantFeaturesConfig {
  tier_features: Partial<Record<Tier, string[]>>;
  upgrade_messages?: Record<string, string>;
}

const TIER_ORDER: Tier[] = ["start", "pro", "expert"];

/** Recursively expand "start" / "pro" references inside the tier's list. */
export function expandTierFeatures(
  config: TenantFeaturesConfig,
  tier: Tier,
  seen: Set<Tier> = new Set(),
): Set<string> {
  if (seen.has(tier)) return new Set();
  seen.add(tier);

  const out = new Set<string>();
  const items = config.tier_features[tier] ?? [];
  for (const item of items) {
    if ((TIER_ORDER as string[]).includes(item)) {
      for (const f of expandTierFeatures(config, item as Tier, seen)) {
        out.add(f);
      }
    } else {
      out.add(item);
    }
  }
  return out;
}

export function hasFeature(
  config: TenantFeaturesConfig,
  tier: Tier | undefined,
  feature: string,
): boolean {
  if (!tier) return false;
  return expandTierFeatures(config, tier).has(feature);
}

export function upgradeMessageFor(
  config: TenantFeaturesConfig,
  feature: string,
): string {
  return (
    config.upgrade_messages?.[feature] ??
    "Эта функция доступна на старшем тарифе."
  );
}
