"use client";

import { MetricCard } from "@/components/ui/Card";
import { CalendarCheck, DollarSign, TrendingUp, Users } from "lucide-react";

interface MainMetricsProps {
  data: {
    total_leads: number;
    leads_change_percent: number;
    total_clients: number;
    clients_change_percent: number;
    total_revenue: number;
    revenue_change_percent: number;
    overall_conversion_rate: number;
    avg_engagement_rate: number;
  };
}

export function MainMetrics({ data }: MainMetricsProps) {
  const metrics = [
    {
      title: "Заявки",
      value: data.total_leads,
      change: data.leads_change_percent,
      icon: Users,
      color: "blue",
    },
    {
      title: "Клиенты",
      value: data.total_clients,
      change: data.clients_change_percent,
      icon: CalendarCheck,
      color: "green",
    },
    {
      title: "Доход",
      value: `${data.total_revenue.toLocaleString()} ₽`,
      change: data.revenue_change_percent,
      icon: DollarSign,
      color: "emerald",
    },
    {
      title: "Конверсия",
      value: `${data.overall_conversion_rate}%`,
      subtitle: `ER: ${data.avg_engagement_rate}%`,
      icon: TrendingUp,
      color: "purple",
    },
  ] as const;

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {metrics.map((metric) => (
        <MetricCard key={metric.title} {...metric} />
      ))}
    </div>
  );
}
