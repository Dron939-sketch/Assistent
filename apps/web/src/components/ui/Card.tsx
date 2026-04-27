import { forwardRef, HTMLAttributes } from "react";
import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "rounded-lg border border-gray-200 bg-white shadow-sm",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
);
Card.displayName = "Card";

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  subtitle?: string;
  icon: LucideIcon;
  color?: "blue" | "green" | "emerald" | "purple" | "orange";
}

const colorClasses = {
  blue: "bg-blue-50 text-blue-600",
  green: "bg-green-50 text-green-600",
  emerald: "bg-emerald-50 text-emerald-600",
  purple: "bg-purple-50 text-purple-600",
  orange: "bg-orange-50 text-orange-600",
};

export function MetricCard({
  title,
  value,
  change,
  subtitle,
  icon: Icon,
  color = "blue",
}: MetricCardProps) {
  return (
    <Card className="p-6">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-gray-500">{title}</p>
        <div className={cn("rounded-full p-2", colorClasses[color])}>
          <Icon className="h-4 w-4" />
        </div>
      </div>
      
      <p className="mt-2 text-2xl font-semibold text-gray-900">{value}</p>
      
      {subtitle && (
        <p className="mt-1 text-xs text-gray-500">{subtitle}</p>
      )}
      
      {change !== undefined && (
        <div className="mt-2 flex items-center gap-1">
          {change > 0 ? (
            <TrendingUp className="h-3 w-3 text-green-600" />
          ) : change < 0 ? (
            <TrendingDown className="h-3 w-3 text-red-600" />
          ) : null}
          <span
            className={cn(
              "text-xs font-medium",
              change > 0
                ? "text-green-600"
                : change < 0
                ? "text-red-600"
                : "text-gray-500"
            )}
          >
            {Math.abs(change)}%
          </span>
          <span className="text-xs text-gray-500">за месяц</span>
        </div>
      )}
    </Card>
  );
}
