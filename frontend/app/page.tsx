"use client";

import { Dashboard } from "@/components/dashboard";

export default function Home() {
  return (
    <main className="min-h-screen p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold">
            Reverso Signal Dashboard
          </h1>
          <p className="text-muted-foreground mt-2">
            Upload time series data and generate AI-powered forecasts
          </p>
        </header>
        <Dashboard />
      </div>
    </main>
  );
}
