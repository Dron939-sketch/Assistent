"use client";

import { ReactNode } from "react";
import { Lock } from "lucide-react";

import {
  TenantFeaturesConfig,
  Tier,
  hasFeature,
  upgradeMessageFor,
} from "@/lib/tier";

interface FeatureGateProps {
  feature: string;
  tier: Tier | undefined;
  config: TenantFeaturesConfig;
  children: ReactNode;
  fallback?: ReactNode;
}

/**
 * Render `children` if the user's tier (within this tenant) has access
 * to `feature`. Otherwise render `fallback` (or a default upgrade card
 * pulled from `config.upgrade_messages`).
 *
 * Once we have a proper auth context, callers can wrap this with a
 * convenience `<Gated feature="post_generator">` that pulls
 * tier+config from React context. Until then the props stay explicit
 * to keep things testable.
 */
export function FeatureGate({
  feature,
  tier,
  config,
  children,
  fallback,
}: FeatureGateProps) {
  if (hasFeature(config, tier, feature)) {
    return <>{children}</>;
  }
  if (fallback !== undefined) return <>{fallback}</>;

  const message = upgradeMessageFor(config, feature);
  return (
    <div className="flex items-start gap-3 rounded-lg border border-dashed border-gray-300 bg-gray-50 p-5 text-sm text-gray-700">
      <Lock className="mt-0.5 h-4 w-4 shrink-0 text-gray-500" />
      <div>
        <p className="font-medium text-gray-900">Функция заблокирована</p>
        <p className="mt-1 text-gray-600">{message}</p>
      </div>
    </div>
  );
}
