"use client";

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { useAuthStore } from "@/store/useAuthStore";

// Components
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";
import { MainMetrics } from "./MainMetrics";
import { LeveragePointCard } from "./LeveragePointCard";
import { ActiveMarathonCard } from "./ActiveMarathonCard";
import { RecentMessagesCard } from "./RecentMessagesCard";
import { ContentCard } from "./ContentCard";
import { LeadsChart } from "./LeadsChart";

export function Dashboard() {
  const { user } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => api.analytics.getDashboard().then((res) => res.data),
    refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
  });

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      <div className="lg:pl-64">
        <Header onMenuClick={() => setSidebarOpen(true)} />
        
        <main className="py-6 px-4 sm:px-6 lg:px-8">
          {/* Main metrics row */}
          {dashboardData && <MainMetrics data={dashboardData} />}
          
          {/* Two columns */}
          <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
            {/* Left column (2/3 width) */}
            <div className="lg:col-span-2 space-y-6">
              <LeadsChart />
              <ContentCard />
            </div>
            
            {/* Right column (1/3 width) */}
            <div className="space-y-6">
              <LeveragePointCard />
              <ActiveMarathonCard />
              <RecentMessagesCard />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
