"use client";

import { UploadComponent } from "@/components/upload";
import { JobResponse } from "@/lib/types";

export default function Home() {
  const handleUploadComplete = (job: JobResponse, data: number[]) => {
    console.log("Upload complete, job_id:", job.job_id, "data points:", data.length);
    // TODO: In Plan 02, this will trigger chart rendering
  };

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Reverso Signal Dashboard</h1>
        <UploadComponent onUploadComplete={handleUploadComplete} />
      </div>
    </main>
  );
}
